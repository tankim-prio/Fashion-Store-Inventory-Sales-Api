import json
import os
import re
import urllib.request
from datetime import date
from decimal import Decimal
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.payment import Payment
from app.models.product import Product
from app.models.product_variant import ProductVariant

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "25"))
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "30m")
AI_OLLAMA_FIRST = os.getenv("AI_OLLAMA_FIRST", "true").lower() == "true"

INTENTS = [
    "business_summary",
    "paid_customers",
    "due_customers",
    "pending_orders",
    "paid_orders",
    "today_sales",
    "total_profit",
    "top_products",
    "low_stock",
    "total_stock",
    "stock_search",
    "recent_customers",
    "find_customer",
    "recent_orders",
    "recent_payments",
    "recent_products",
    "business_calculation",
    "general_business_question",
    "help",
    "unknown",
]


def to_float(value):
    if value is None:
        return 0.0

    if isinstance(value, Decimal):
        return float(value)

    try:
        return float(value)
    except Exception:
        return 0.0


def money(value):
    return round(to_float(value), 2)


def normalize_text(text: str):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9@\+\-\s\.]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def contains_any(text: str, words: list[str]):
    return any(word in text for word in words)


def extract_number(text: str):
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


def extract_sku(text: str):
    tokens = re.findall(r"[a-zA-Z0-9-]{4,}", text)

    for token in tokens:
        if "-" in token:
            return token

    return None


def extract_customer_keyword(text: str):
    phone = re.search(r"\+?\d{5,20}", text)

    if phone:
        return phone.group()

    cleaned = normalize_text(text)

    remove_words = [
        "find", "search", "customer", "name", "phone", "email",
        "show", "give", "me", "details", "of", "the", "a", "an",
    ]

    for word in remove_words:
        cleaned = cleaned.replace(word, "")

    cleaned = cleaned.strip()
    return cleaned or None


def suggestions():
    return [
        "business summary",
        "who bought products and paid?",
        "paid customers name and phone",
        "which customers have no due?",
        "who still needs to pay?",
        "today sales",
        "total profit",
        "which products need restock?",
        "total stock value",
        "top selling products",
        "If 22 t-shirts cost 450 each, what is total cost?",
        "find customer 01711111111",
    ]


def table_data(title, columns, rows, totals=None):
    return {
        "type": "table",
        "title": title,
        "columns": columns,
        "rows": rows,
        "totals": totals or {},
    }


def metric_data(title, metrics):
    return {
        "type": "metrics",
        "title": title,
        "metrics": metrics,
    }


def intent_result(intent, confidence, threshold=None, sku=None, customer_keyword=None, source="unknown"):
    return {
        "intent": intent,
        "confidence": confidence,
        "threshold": threshold,
        "sku": sku,
        "customer_keyword": customer_keyword,
        "source": source,
    }


def safe_json_from_text(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError("No JSON found from Ollama response")

    return json.loads(match.group())


def quick_detect_intent(question: str):
    q = normalize_text(question)

    threshold = extract_number(q)
    sku = extract_sku(question)
    customer_keyword = extract_customer_keyword(question)

    if q in ["hi", "hello", "help", "what can you do", "what can you do"]:
        return intent_result("help", 1.0, threshold, sku, customer_keyword, "fast_rules")

    if contains_any(q, ["summary", "overview", "business condition", "shop report", "dashboard report", "overall shop"]):
        return intent_result("business_summary", 0.95, threshold, sku, customer_keyword, "fast_rules")

    if contains_any(q, ["paid customer", "paid customers", "paid buyer", "paid buyers", "completed payment", "payment completed", "fully paid", "no due", "clear payment"]):
        return intent_result("paid_customers", 0.98, threshold, sku, customer_keyword, "fast_rules")

    if "who bought" in q and "paid" in q:
        return intent_result("paid_customers", 0.98, threshold, sku, customer_keyword, "fast_rules")

    if "customers" in q and "no due" in q:
        return intent_result("paid_customers", 0.98, threshold, sku, customer_keyword, "fast_rules")

    if contains_any(q, ["unpaid", "due customer", "due customers", "due payment", "not paid", "still needs to pay", "still need to pay", "needs to pay"]):
        return intent_result("due_customers", 0.98, threshold, sku, customer_keyword, "fast_rules")

    if "pending" in q and "order" in q:
        return intent_result("pending_orders", 0.95, threshold, sku, customer_keyword, "fast_rules")

    if "paid" in q and "order" in q:
        return intent_result("paid_orders", 0.95, threshold, sku, customer_keyword, "fast_rules")

    if "today" in q and contains_any(q, ["sale", "sales", "sell", "order", "orders"]):
        return intent_result("today_sales", 0.95, threshold, sku, customer_keyword, "fast_rules")

    if contains_any(q, ["profit", "revenue", "income", "margin", "earning", "earnings"]):
        return intent_result("total_profit", 0.95, threshold, sku, customer_keyword, "fast_rules")

    if contains_any(q, ["top product", "top products", "best selling", "most sold", "popular product", "popular products", "best product"]):
        return intent_result("top_products", 0.95, threshold, sku, customer_keyword, "fast_rules")

    if contains_any(q, ["low stock", "restock", "shortage", "running out", "need stock", "need restock"]):
        return intent_result("low_stock", 0.95, threshold, sku, customer_keyword, "fast_rules")

    if contains_any(q, ["total stock", "stock value", "inventory value", "available stock", "all stock"]):
        return intent_result("total_stock", 0.95, threshold, sku, customer_keyword, "fast_rules")

    if "stock" in q and (sku or "sku" in q or "item code" in q or "product code" in q):
        return intent_result("stock_search", 0.90, threshold, sku, customer_keyword, "fast_rules")

    if "find customer" in q or "search customer" in q:
        return intent_result("find_customer", 0.95, threshold, sku, customer_keyword, "fast_rules")

    if "payment" in q or "payments" in q:
        return intent_result("recent_payments", 0.85, threshold, sku, customer_keyword, "fast_rules")

    if "customer" in q or "customers" in q:
        return intent_result("recent_customers", 0.80, threshold, sku, customer_keyword, "fast_rules")

    if "product" in q or "products" in q:
        return intent_result("recent_products", 0.80, threshold, sku, customer_keyword, "fast_rules")

    if "order" in q or "orders" in q:
        return intent_result("recent_orders", 0.80, threshold, sku, customer_keyword, "fast_rules")

    math_words = [
        "calculate", "calculation", "total cost", "total price", "how much",
        "pieces", "piece", "pcs", "unit price", "buy price", "sell price",
        "profit if", "margin if", "discount", "percent", "percentage",
    ]

    numbers = re.findall(r"\d+(?:\.\d+)?", q)

    if len(numbers) >= 2 and contains_any(q, math_words):
        return intent_result("business_calculation", 0.85, threshold, sku, customer_keyword, "fast_rules")

    return None


@lru_cache(maxsize=300)
def ollama_detect_cached(question: str):
    prompt = f"""
You are an intent detector for a Fashion Store Inventory and Sales Management chatbot.

Return ONLY JSON. No markdown. No explanation.

Allowed intents:
business_summary, paid_customers, due_customers, pending_orders, paid_orders,
today_sales, total_profit, top_products, low_stock, total_stock, stock_search,
recent_customers, find_customer, recent_orders, recent_payments, recent_products,
business_calculation, general_business_question, help, unknown.

Mappings:
- who bought products and paid = paid_customers
- customers with no due = paid_customers
- completed payment customers = paid_customers
- paid buyer list = paid_customers
- who still needs to pay = due_customers
- unpaid customers = due_customers
- products need restock = low_stock
- running out of stock = low_stock
- best products = top_products
- overall shop report = business_summary
- any calculation using pieces, price, cost, discount, profit, total amount = business_calculation
- general fashion store advice or explanation = general_business_question

JSON shape:
{{
  "intent": "one_intent",
  "confidence": 0.0,
  "threshold": null,
  "sku": null,
  "customer_keyword": null
}}

Question: {question}
""".strip()

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "keep_alive": OLLAMA_KEEP_ALIVE,
        "options": {
            "temperature": 0,
            "num_predict": 120,
            "num_ctx": 1024,
        },
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
        result = json.loads(response.read().decode("utf-8"))

    raw_text = result.get("response", "").strip()
    parsed = safe_json_from_text(raw_text)

    intent = parsed.get("intent", "unknown")

    if intent not in INTENTS:
        intent = "unknown"

    return intent_result(
        intent=intent,
        confidence=to_float(parsed.get("confidence", 0)),
        threshold=parsed.get("threshold"),
        sku=parsed.get("sku"),
        customer_keyword=parsed.get("customer_keyword"),
        source="ollama_local_ai",
    )


def detect_intent(question: str):
    if AI_OLLAMA_FIRST:
        try:
            detected = ollama_detect_cached(normalize_text(question))

            if detected["intent"] != "unknown":
                return detected
        except Exception:
            pass

    fast = quick_detect_intent(question)

    if fast:
        return fast

    try:
        return ollama_detect_cached(normalize_text(question))
    except Exception:
        return intent_result("general_business_question", 0.50, source="fallback_general")


def get_customer(db: Session, customer_id: int):
    return db.get(Customer, customer_id) if customer_id else None


def get_product(db: Session, product_id: int):
    return db.get(Product, product_id) if product_id else None


def get_variant(db: Session, variant_id: int):
    return db.get(ProductVariant, variant_id) if variant_id else None


def is_cancelled_order(order: Order):
    return order.status in ["cancelled", "refunded"]


def get_paid_amount(db: Session, order: Order):
    payments = (
        db.query(Payment)
        .filter(Payment.order_id == order.id)
        .filter(Payment.status == "paid")
        .all()
    )

    paid_amount = sum(to_float(payment.amount) for payment in payments)

    if paid_amount <= 0 and order.status == "paid":
        paid_amount = to_float(order.final_amount)

    return paid_amount


def get_order_due(db: Session, order: Order):
    final_amount = to_float(order.final_amount)
    paid_amount = get_paid_amount(db, order)
    due_amount = max(final_amount - paid_amount, 0)

    return paid_amount, due_amount


def is_paid_order(db: Session, order: Order):
    paid_amount, due_amount = get_order_due(db, order)
    final_amount = to_float(order.final_amount)

    return (
        order.status == "paid"
        or paid_amount >= final_amount
        or (due_amount <= 0 and final_amount > 0)
    )


def get_paid_orders(db: Session):
    orders = db.query(Order).order_by(Order.id.desc()).all()

    return [
        order for order in orders
        if not is_cancelled_order(order) and is_paid_order(db, order)
    ]


def get_due_orders(db: Session):
    orders = db.query(Order).order_by(Order.id.desc()).all()
    due_orders = []

    for order in orders:
        if is_cancelled_order(order):
            continue

        _, due_amount = get_order_due(db, order)

        if due_amount > 0:
            due_orders.append(order)

    return due_orders


def order_customer_row(db: Session, order: Order):
    customer = get_customer(db, order.customer_id)
    paid_amount, due_amount = get_order_due(db, order)

    return {
        "customer_name": customer.name if customer else "Unknown customer",
        "phone": customer.phone if customer else "",
        "email": customer.email if customer else "",
        "order_number": order.order_number,
        "final_amount": money(order.final_amount),
        "paid_amount": money(paid_amount),
        "due_amount": money(due_amount),
        "order_status": order.status,
        "created_at": str(order.created_at) if order.created_at else "",
    }


def order_row(db: Session, order: Order):
    customer = get_customer(db, order.customer_id)
    paid_amount, due_amount = get_order_due(db, order)

    return {
        "order_number": order.order_number,
        "customer_name": customer.name if customer else "Unknown customer",
        "phone": customer.phone if customer else "",
        "final_amount": money(order.final_amount),
        "paid_amount": money(paid_amount),
        "due_amount": money(due_amount),
        "status": order.status,
        "created_by": order.created_by,
        "created_at": str(order.created_at) if order.created_at else "",
    }


def customer_row(customer: Customer):
    return {
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email or "",
        "address": customer.address or "",
        "active": customer.is_active,
    }


def product_row(product: Product):
    return {
        "id": product.id,
        "name": product.name,
        "category_id": product.category_id,
        "brand": product.brand or "",
        "description": product.description or "",
        "active": product.is_active,
    }


def payment_row(db: Session, payment: Payment):
    order = db.get(Order, payment.order_id)
    customer = get_customer(db, order.customer_id) if order else None

    return {
        "payment_id": payment.id,
        "order_number": order.order_number if order else "",
        "customer_name": customer.name if customer else "",
        "phone": customer.phone if customer else "",
        "method": payment.payment_method,
        "amount": money(payment.amount),
        "status": payment.status,
        "transaction_id": payment.transaction_id or "",
        "paid_at": str(payment.paid_at) if payment.paid_at else "",
    }


def stock_row(db: Session, variant: ProductVariant):
    product = get_product(db, variant.product_id)

    return {
        "product_name": product.name if product else "Unknown product",
        "sku": variant.sku,
        "size": variant.size,
        "color": variant.color,
        "stock_quantity": variant.stock_quantity,
        "buy_price": money(variant.buy_price),
        "sell_price": money(variant.sell_price),
    }


def answer_help():
    return {
        "answer": "I use free local Ollama to understand questions, then I answer from your database or solve fashion-store business calculations.",
        "data": metric_data(
            "AI Assistant Mode",
            {
                "mode": "Ollama-first + safe database queries",
                "model": OLLAMA_MODEL,
                "cost": "0 taka",
                "can_answer": "database questions + business calculations + store advice",
            },
        ),
        "suggestions": suggestions(),
    }


def answer_business_summary(db: Session):
    products = db.query(Product).all()
    variants = db.query(ProductVariant).all()
    customers = db.query(Customer).all()
    orders = db.query(Order).all()

    paid_orders = get_paid_orders(db)
    due_orders = get_due_orders(db)

    total_stock = sum(item.stock_quantity for item in variants)
    low_stock_count = len([item for item in variants if item.stock_quantity <= 5])
    total_paid_sales = sum(to_float(order.final_amount) for order in paid_orders)

    total_due = 0
    for order in due_orders:
        _, due = get_order_due(db, order)
        total_due += due

    return {
        "answer": f"Your business has {len(products)} product(s), {len(variants)} variant(s), {total_stock} stock item(s), {len(customers)} customer(s), {len(orders)} order(s), {len(paid_orders)} paid order(s), and {len(due_orders)} due order(s). Total paid sales is {money(total_paid_sales)} and total due is {money(total_due)}.",
        "data": metric_data(
            "Business Summary",
            {
                "products": len(products),
                "variants": len(variants),
                "total_stock": total_stock,
                "customers": len(customers),
                "orders": len(orders),
                "paid_orders": len(paid_orders),
                "due_orders": len(due_orders),
                "low_stock_variants": low_stock_count,
                "total_paid_sales": money(total_paid_sales),
                "total_due": money(total_due),
            },
        ),
        "suggestions": suggestions(),
    }


def answer_paid_customers(db: Session):
    paid_orders = get_paid_orders(db)
    rows = [order_customer_row(db, order) for order in paid_orders]

    unique_customers = set()
    for row in rows:
        key = row["phone"] or row["email"] or row["customer_name"]
        unique_customers.add(key)

    total_final = sum(row["final_amount"] for row in rows)
    total_paid = sum(row["paid_amount"] for row in rows)

    return {
        "answer": f"You have {len(unique_customers)} paid customer(s) from {len(rows)} paid order(s). Total final amount is {money(total_final)} and total paid amount is {money(total_paid)}." if rows else "No paid customer found yet.",
        "data": table_data(
            "Paid Customers",
            [
                "customer_name",
                "phone",
                "email",
                "order_number",
                "final_amount",
                "paid_amount",
                "due_amount",
                "order_status",
                "created_at",
            ],
            rows,
            {
                "unique_paid_customers": len(unique_customers),
                "paid_orders": len(rows),
                "total_final_amount": money(total_final),
                "total_paid": money(total_paid),
            },
        ),
        "suggestions": suggestions(),
    }


def answer_due_customers(db: Session):
    due_orders = get_due_orders(db)
    rows = [order_customer_row(db, order) for order in due_orders]
    total_due = sum(row["due_amount"] for row in rows)

    return {
        "answer": f"You have {len(rows)} due order(s). Total due amount is {money(total_due)}." if rows else "No due customer found. All valid orders look fully paid.",
        "data": table_data(
            "Due Customers",
            [
                "customer_name",
                "phone",
                "email",
                "order_number",
                "final_amount",
                "paid_amount",
                "due_amount",
                "order_status",
            ],
            rows,
            {
                "due_orders": len(rows),
                "total_due": money(total_due),
            },
        ),
        "suggestions": suggestions(),
    }


def answer_orders_by_status(db: Session, status=None):
    if status == "paid":
        orders = get_paid_orders(db)
        title = "Paid Orders"
    elif status == "pending":
        orders = (
            db.query(Order)
            .filter(Order.status == "pending")
            .order_by(Order.id.desc())
            .all()
        )
        title = "Pending Orders"
    else:
        orders = db.query(Order).order_by(Order.id.desc()).limit(20).all()
        title = "Recent Orders"

    rows = [order_row(db, order) for order in orders]

    total_final = sum(row["final_amount"] for row in rows)
    total_paid = sum(row["paid_amount"] for row in rows)
    total_due = sum(row["due_amount"] for row in rows)

    return {
        "answer": f"I found {len(rows)} order(s). Total final amount is {money(total_final)}, paid is {money(total_paid)}, and due is {money(total_due)}.",
        "data": table_data(
            title,
            [
                "order_number",
                "customer_name",
                "phone",
                "final_amount",
                "paid_amount",
                "due_amount",
                "status",
                "created_at",
            ],
            rows,
            {
                "orders": len(rows),
                "total_final_amount": money(total_final),
                "total_paid": money(total_paid),
                "total_due": money(total_due),
            },
        ),
        "suggestions": suggestions(),
    }


def answer_today_sales(db: Session):
    today = date.today()
    orders = db.query(Order).all()

    today_orders = [
        order for order in orders
        if order.created_at
        and order.created_at.date() == today
        and not is_cancelled_order(order)
    ]

    rows = [order_row(db, order) for order in today_orders]

    total_sales = sum(row["final_amount"] for row in rows)
    total_paid = sum(row["paid_amount"] for row in rows)
    total_due = sum(row["due_amount"] for row in rows)

    return {
        "answer": f"Today you have {len(rows)} order(s). Total sales is {money(total_sales)}, paid is {money(total_paid)}, and due is {money(total_due)}.",
        "data": table_data(
            "Today Sales",
            [
                "order_number",
                "customer_name",
                "phone",
                "final_amount",
                "paid_amount",
                "due_amount",
                "status",
                "created_at",
            ],
            rows,
            {
                "date": str(today),
                "today_orders": len(rows),
                "total_sales": money(total_sales),
                "total_paid": money(total_paid),
                "total_due": money(total_due),
            },
        ),
        "suggestions": suggestions(),
    }


def answer_profit(db: Session):
    orders = [
        order for order in db.query(Order).all()
        if not is_cancelled_order(order)
    ]

    total_revenue = 0
    total_cost = 0
    total_discount = 0
    sold_items = 0

    for order in orders:
        total_discount += to_float(order.discount)

        order_items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        for item in order_items:
            variant = get_variant(db, item.variant_id)

            if not variant:
                continue

            total_revenue += to_float(item.total_price)
            total_cost += to_float(variant.buy_price) * item.quantity
            sold_items += item.quantity

    estimated_profit = total_revenue - total_discount - total_cost

    return {
        "answer": f"Estimated profit is {money(estimated_profit)}. Revenue is {money(total_revenue)}, cost is {money(total_cost)}, and discount is {money(total_discount)}.",
        "data": metric_data(
            "Profit Summary",
            {
                "orders_counted": len(orders),
                "sold_items": sold_items,
                "total_revenue": money(total_revenue),
                "total_cost": money(total_cost),
                "total_discount": money(total_discount),
                "estimated_profit": money(estimated_profit),
            },
        ),
        "suggestions": suggestions(),
    }


def answer_top_products(db: Session):
    order_items = db.query(OrderItem).all()
    sales_map = {}

    for item in order_items:
        order = db.get(Order, item.order_id)

        if order and is_cancelled_order(order):
            continue

        variant = get_variant(db, item.variant_id)

        if not variant:
            continue

        product = get_product(db, variant.product_id)
        product_name = product.name if product else f"Product {variant.product_id}"

        if product_name not in sales_map:
            sales_map[product_name] = {
                "product_name": product_name,
                "quantity_sold": 0,
                "total_sales": 0,
                "sku_examples": set(),
            }

        sales_map[product_name]["quantity_sold"] += item.quantity
        sales_map[product_name]["total_sales"] += to_float(item.total_price)

        if variant.sku:
            sales_map[product_name]["sku_examples"].add(variant.sku)

    rows = []
    for item in sales_map.values():
        rows.append({
            "product_name": item["product_name"],
            "quantity_sold": item["quantity_sold"],
            "total_sales": money(item["total_sales"]),
            "sku_examples": ", ".join(list(item["sku_examples"])[:3]),
        })

    rows = sorted(rows, key=lambda item: item["quantity_sold"], reverse=True)[:10]

    return {
        "answer": f"Here are your top {len(rows)} selling product(s)." if rows else "No selling product data found yet.",
        "data": table_data(
            "Top Products",
            ["product_name", "quantity_sold", "total_sales", "sku_examples"],
            rows,
            {
                "products_found": len(rows),
            },
        ),
        "suggestions": suggestions(),
    }


def answer_low_stock(db: Session, threshold=None):
    threshold = int(threshold) if threshold else 5

    variants = (
        db.query(ProductVariant)
        .filter(ProductVariant.stock_quantity <= threshold)
        .order_by(ProductVariant.stock_quantity.asc())
        .all()
    )

    rows = [stock_row(db, variant) for variant in variants]

    return {
        "answer": f"You have {len(rows)} low-stock variant(s) with stock less than or equal to {threshold}.",
        "data": table_data(
            "Low Stock Products",
            [
                "product_name",
                "sku",
                "size",
                "color",
                "stock_quantity",
                "buy_price",
                "sell_price",
            ],
            rows,
            {
                "threshold": threshold,
                "low_stock_variants": len(rows),
            },
        ),
        "suggestions": suggestions(),
    }


def answer_total_stock(db: Session):
    variants = db.query(ProductVariant).all()
    rows = [stock_row(db, variant) for variant in variants]

    total_stock = sum(variant.stock_quantity for variant in variants)
    buy_value = sum(to_float(variant.buy_price) * variant.stock_quantity for variant in variants)
    sell_value = sum(to_float(variant.sell_price) * variant.stock_quantity for variant in variants)

    return {
        "answer": f"Total available stock is {total_stock} item(s) across {len(variants)} variant(s). Estimated selling value is {money(sell_value)}.",
        "data": table_data(
            "Total Stock",
            [
                "product_name",
                "sku",
                "size",
                "color",
                "stock_quantity",
                "buy_price",
                "sell_price",
            ],
            rows,
            {
                "total_stock": total_stock,
                "total_variants": len(variants),
                "estimated_buy_value": money(buy_value),
                "estimated_selling_value": money(sell_value),
            },
        ),
        "suggestions": suggestions(),
    }


def answer_stock_search(db: Session, question: str, sku=None):
    variants = db.query(ProductVariant).all()
    matched = []

    if sku:
        sku_lower = str(sku).lower()
        matched = [
            variant for variant in variants
            if variant.sku and sku_lower in variant.sku.lower()
        ]

    if not matched:
        tokens = re.findall(r"[a-zA-Z0-9-]{3,}", question)

        for variant in variants:
            product = get_product(db, variant.product_id)
            product_name = product.name.lower() if product and product.name else ""
            sku_text = variant.sku.lower() if variant.sku else ""
            color_text = variant.color.lower() if variant.color else ""
            size_text = variant.size.lower() if variant.size else ""

            searchable = f"{product_name} {sku_text} {color_text} {size_text}"

            if any(token.lower() in searchable for token in tokens):
                matched.append(variant)

    unique = []
    seen = set()

    for item in matched:
        if item.id not in seen:
            unique.append(item)
            seen.add(item.id)

    rows = [stock_row(db, variant) for variant in unique]

    return {
        "answer": f"I found {len(rows)} matching stock result(s)." if rows else "I could not find any stock item matching your question.",
        "data": table_data(
            "Stock Search Result",
            [
                "product_name",
                "sku",
                "size",
                "color",
                "stock_quantity",
                "buy_price",
                "sell_price",
            ],
            rows,
        ),
        "suggestions": suggestions(),
    }


def answer_recent_customers(db: Session):
    customers = db.query(Customer).order_by(Customer.id.desc()).limit(20).all()
    rows = [customer_row(customer) for customer in customers]

    return {
        "answer": f"Here are the latest {len(rows)} customer(s).",
        "data": table_data(
            "Recent Customers",
            ["name", "phone", "email", "address", "active"],
            rows,
            {
                "customers": len(rows),
            },
        ),
        "suggestions": suggestions(),
    }


def answer_find_customer(db: Session, question: str, keyword=None):
    if not keyword:
        keyword = extract_customer_keyword(question)

    if not keyword:
        return answer_recent_customers(db)

    customers = (
        db.query(Customer)
        .filter(
            or_(
                Customer.name.ilike(f"%{keyword}%"),
                Customer.phone.ilike(f"%{keyword}%"),
                Customer.email.ilike(f"%{keyword}%"),
            )
        )
        .order_by(Customer.id.desc())
        .all()
    )

    rows = [customer_row(customer) for customer in customers]

    return {
        "answer": f"I found {len(rows)} customer(s) matching '{keyword}'." if rows else f"No customer found matching '{keyword}'.",
        "data": table_data(
            "Customer Search Result",
            ["name", "phone", "email", "address", "active"],
            rows,
        ),
        "suggestions": suggestions(),
    }


def answer_recent_payments(db: Session):
    payments = db.query(Payment).order_by(Payment.id.desc()).limit(20).all()
    rows = [payment_row(db, payment) for payment in payments]

    total_amount = sum(row["amount"] for row in rows)

    return {
        "answer": f"Here are the latest {len(rows)} payment record(s). Total amount in this list is {money(total_amount)}.",
        "data": table_data(
            "Recent Payments",
            [
                "payment_id",
                "order_number",
                "customer_name",
                "phone",
                "method",
                "amount",
                "status",
                "transaction_id",
                "paid_at",
            ],
            rows,
            {
                "payments": len(rows),
                "total_amount": money(total_amount),
            },
        ),
        "suggestions": suggestions(),
    }


def answer_recent_products(db: Session):
    products = db.query(Product).order_by(Product.id.desc()).limit(20).all()
    rows = [product_row(product) for product in products]

    return {
        "answer": f"Here are the latest {len(rows)} product(s).",
        "data": table_data(
            "Recent Products",
            ["id", "name", "category_id", "brand", "description", "active"],
            rows,
            {
                "products": len(rows),
            },
        ),
        "suggestions": suggestions(),
    }


def payment_row(db: Session, payment: Payment):
    order = db.get(Order, payment.order_id)
    customer = get_customer(db, order.customer_id) if order else None

    return {
        "payment_id": payment.id,
        "order_number": order.order_number if order else "",
        "customer_name": customer.name if customer else "",
        "phone": customer.phone if customer else "",
        "method": payment.payment_method,
        "amount": money(payment.amount),
        "status": payment.status,
        "transaction_id": payment.transaction_id or "",
        "paid_at": str(payment.paid_at) if payment.paid_at else "",
    }


def get_compact_database_context(db: Session):
    products_count = db.query(Product).count()
    variants = db.query(ProductVariant).all()
    customers_count = db.query(Customer).count()
    orders_count = db.query(Order).count()
    payments_count = db.query(Payment).count()

    total_stock = sum(item.stock_quantity for item in variants)

    return {
        "products_count": products_count,
        "variants_count": len(variants),
        "customers_count": customers_count,
        "orders_count": orders_count,
        "payments_count": payments_count,
        "total_stock": total_stock,
        "currency": "BDT",
    }


def call_ollama_general_answer(db: Session, question: str):
    context = get_compact_database_context(db)

    prompt = f"""
You are the AI Assistant inside a Fashion Store Inventory & Sales Management dashboard.

You must answer the user's question clearly and professionally.

Rules:
- If the question is a calculation, calculate it correctly.
- If the user gives quantity and unit price, multiply them.
- If the user asks fashion-store business advice, answer with practical advice.
- If the user asks database-specific information that is not in the provided context, do not invent data.
- Do not claim a customer/product/order exists unless it is from the database context.
- Keep answer short, organized, and easy to understand.
- Use BDT when money is mentioned.
- Return ONLY valid JSON. No markdown.

Database context:
{json.dumps(context, indent=2)}

Return JSON:
{{
  "answer": "well organized answer",
  "metrics": {{
    "optional_key": "optional_value"
  }}
}}

User question:
{question}
""".strip()

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "keep_alive": OLLAMA_KEEP_ALIVE,
        "options": {
            "temperature": 0.1,
            "num_predict": 350,
            "num_ctx": 2048,
        },
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
        result = json.loads(response.read().decode("utf-8"))

    raw_text = result.get("response", "").strip()
    parsed = safe_json_from_text(raw_text)

    answer = parsed.get("answer", "I could not prepare a proper answer.")
    metrics = parsed.get("metrics") or {}

    data = None
    if isinstance(metrics, dict) and metrics:
        data = metric_data("Answer Summary", metrics)

    return {
        "answer": answer,
        "data": data,
        "suggestions": suggestions(),
    }


def answer_general_or_calculation(db: Session, question: str):
    try:
        return call_ollama_general_answer(db, question)
    except Exception:
        return {
            "answer": "I could not process that question with Ollama right now. Please make sure Ollama is running, then ask again.",
            "data": metric_data(
                "Troubleshooting",
                {
                    "check_1": "Run: ollama list",
                    "check_2": "Run: ollama run qwen2.5:3b",
                    "check_3": "Restart FastAPI server",
                },
            ),
            "suggestions": suggestions(),
        }


def answer_ai_question(db: Session, question: str):
    detected = detect_intent(question)
    intent = detected.get("intent", "unknown")

    if intent == "help":
        response = answer_help()
    elif intent == "business_summary":
        response = answer_business_summary(db)
    elif intent == "paid_customers":
        response = answer_paid_customers(db)
    elif intent == "due_customers":
        response = answer_due_customers(db)
    elif intent == "pending_orders":
        response = answer_orders_by_status(db, "pending")
    elif intent == "paid_orders":
        response = answer_orders_by_status(db, "paid")
    elif intent == "today_sales":
        response = answer_today_sales(db)
    elif intent == "total_profit":
        response = answer_profit(db)
    elif intent == "top_products":
        response = answer_top_products(db)
    elif intent == "low_stock":
        response = answer_low_stock(db, detected.get("threshold"))
    elif intent == "total_stock":
        response = answer_total_stock(db)
    elif intent == "stock_search":
        response = answer_stock_search(db, question, detected.get("sku"))
    elif intent == "recent_customers":
        response = answer_recent_customers(db)
    elif intent == "find_customer":
        response = answer_find_customer(db, question, detected.get("customer_keyword"))
    elif intent == "recent_orders":
        response = answer_orders_by_status(db)
    elif intent == "recent_payments":
        response = answer_recent_payments(db)
    elif intent == "recent_products":
        response = answer_recent_products(db)
    elif intent in ["business_calculation", "general_business_question", "unknown"]:
        response = answer_general_or_calculation(db, question)
    else:
        response = answer_general_or_calculation(db, question)

    return response
