from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from math import ceil

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.product_variant import ProductVariant


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


def safe_date(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return None


def get_customer(db: Session, customer_id: int):
    return db.get(Customer, customer_id) if customer_id else None


def get_product(db: Session, product_id: int):
    return db.get(Product, product_id) if product_id else None


def get_variant(db: Session, variant_id: int):
    return db.get(ProductVariant, variant_id) if variant_id else None


def valid_orders(db: Session):
    orders = db.query(Order).order_by(Order.created_at.asc()).all()

    return [
        order for order in orders
        if order.status not in ["cancelled", "refunded"]
    ]


def product_is_active(product: Product):
    if hasattr(product, "is_active"):
        return bool(product.is_active)

    return True


def variant_label(db: Session, variant: ProductVariant):
    product = get_product(db, variant.product_id)

    return {
        "product_name": product.name if product else "Unknown product",
        "sku": variant.sku or "",
        "size": variant.size or "",
        "color": variant.color or "",
        "category_id": product.category_id if product else None,
        "brand": product.brand if product and product.brand else "",
    }


def get_daily_sales_map(db: Session, lookback_days: int = 30):
    lookback_days = max(7, min(int(lookback_days), 90))

    today = date.today()
    start_date = today - timedelta(days=lookback_days - 1)

    daily_sales = {
        start_date + timedelta(days=i): 0.0
        for i in range(lookback_days)
    }

    for order in valid_orders(db):
        order_date = safe_date(order.created_at)

        if order_date and start_date <= order_date <= today:
            daily_sales[order_date] += to_float(order.final_amount)

    return daily_sales


def linear_forecast(values: list[float], days: int):
    days = max(1, min(int(days), 30))

    if not values:
        return [0.0 for _ in range(days)]

    if len(values) == 1:
        return [max(values[0], 0) for _ in range(days)]

    n = len(values)
    x_values = list(range(n))
    y_values = values

    x_mean = sum(x_values) / n
    y_mean = sum(y_values) / n

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)

    slope = numerator / denominator if denominator else 0
    intercept = y_mean - slope * x_mean

    forecast = []

    for i in range(days):
        next_x = n + i
        predicted = intercept + slope * next_x
        forecast.append(max(predicted, 0))

    return forecast


def sales_forecast(db: Session, forecast_days: int = 7, lookback_days: int = 30):
    forecast_days = max(1, min(int(forecast_days), 30))
    lookback_days = max(7, min(int(lookback_days), 90))

    daily_sales = get_daily_sales_map(db, lookback_days=lookback_days)
    values = list(daily_sales.values())

    average_daily_sales = sum(values) / len(values) if values else 0
    forecast_values = linear_forecast(values, forecast_days)

    today = date.today()
    rows = []

    for i, predicted_amount in enumerate(forecast_values, start=1):
        rows.append({
            "forecast_date": str(today + timedelta(days=i)),
            "predicted_sales_bdt": money(predicted_amount),
            "method": "Recent sales trend",
        })

    total_forecast = sum(forecast_values)
    active_sales_days = len([value for value in values if value > 0])

    confidence = "low"

    if active_sales_days >= 20:
        confidence = "high"
    elif active_sales_days >= 7:
        confidence = "medium"

    return {
        "title": "Sales Forecast",
        "summary": f"Next {forecast_days} day(s) predicted sales is {money(total_forecast)} BDT. This is based on the previous {lookback_days} day(s) order history.",
        "data": {
            "metrics": {
                "forecast_days": forecast_days,
                "previous_sales_data_days": lookback_days,
                "average_daily_sales_bdt": money(average_daily_sales),
                "predicted_total_sales_bdt": money(total_forecast),
                "active_sales_days": active_sales_days,
                "confidence": confidence,
            },
            "rows": rows,
        },
    }


def get_variant_sales_velocity(db: Session, lookback_days: int = 30):
    lookback_days = max(7, min(int(lookback_days), 90))

    today = date.today()
    start_date = today - timedelta(days=lookback_days - 1)

    valid_order_ids = []

    for order in valid_orders(db):
        order_date = safe_date(order.created_at)

        if order_date and start_date <= order_date <= today:
            valid_order_ids.append(order.id)

    velocity = defaultdict(lambda: {
        "quantity_sold": 0,
        "sales_amount": 0.0,
    })

    if not valid_order_ids:
        return velocity

    items = db.query(OrderItem).filter(OrderItem.order_id.in_(valid_order_ids)).all()

    for item in items:
        velocity[item.variant_id]["quantity_sold"] += item.quantity
        velocity[item.variant_id]["sales_amount"] += to_float(item.total_price)

    return velocity


def low_stock_prediction(db: Session, lookback_days: int = 30):
    lookback_days = max(7, min(int(lookback_days), 90))

    velocity = get_variant_sales_velocity(db, lookback_days=lookback_days)
    variants = db.query(ProductVariant).order_by(ProductVariant.stock_quantity.asc()).all()

    rows = []

    for variant in variants:
        sold_qty = velocity[variant.id]["quantity_sold"]
        current_stock = variant.stock_quantity or 0
        avg_daily_sales_qty = sold_qty / lookback_days

        if avg_daily_sales_qty > 0:
            days_remaining = current_stock / avg_daily_sales_qty
        else:
            days_remaining = None

        risk_level = "Safe"
        action = "No urgent action"

        if days_remaining is not None and days_remaining <= 7:
            risk_level = "High"
            action = "Restock soon"
        elif days_remaining is not None and days_remaining <= 14:
            risk_level = "Medium"
            action = "Monitor closely"
        elif current_stock <= 5:
            risk_level = "Medium"
            action = "Monitor closely"

        if risk_level in ["High", "Medium"] or current_stock <= 5:
            info = variant_label(db, variant)

            rows.append({
                "product_name": info["product_name"],
                "sku": info["sku"],
                "size": info["size"],
                "color": info["color"],
                "current_stock": current_stock,
                "sold_last_days": sold_qty,
                "avg_daily_sales_qty": round(avg_daily_sales_qty, 2),
                "estimated_days_remaining": round(days_remaining, 1) if days_remaining is not None else "No recent sales",
                "risk_level": risk_level,
                "recommended_action": action,
            })

    rows = sorted(
        rows,
        key=lambda item: (
            0 if item["risk_level"] == "High" else 1,
            item["current_stock"],
        )
    )

    high_risk = len([row for row in rows if row["risk_level"] == "High"])
    medium_risk = len([row for row in rows if row["risk_level"] == "Medium"])

    return {
        "title": "Stock Risk Prediction",
        "summary": f"{high_risk} high-risk item(s) and {medium_risk} medium-risk item(s) found using previous {lookback_days} day(s) sales speed.",
        "data": {
            "metrics": {
                "previous_sales_data_days": lookback_days,
                "high_risk_items": high_risk,
                "medium_risk_items": medium_risk,
                "total_flagged_items": len(rows),
            },
            "rows": rows,
        },
    }


def reorder_recommendations(db: Session, lookback_days: int = 30, lead_time_days: int = 7, safety_days: int = 5):
    lookback_days = max(7, min(int(lookback_days), 90))
    lead_time_days = max(1, min(int(lead_time_days), 60))
    safety_days = max(1, min(int(safety_days), 60))

    velocity = get_variant_sales_velocity(db, lookback_days=lookback_days)
    variants = db.query(ProductVariant).order_by(ProductVariant.stock_quantity.asc()).all()

    rows = []

    for variant in variants:
        current_stock = variant.stock_quantity or 0
        sold_qty = velocity[variant.id]["quantity_sold"]
        avg_daily_sales_qty = sold_qty / lookback_days

        target_stock = ceil(avg_daily_sales_qty * (lead_time_days + safety_days))

        if avg_daily_sales_qty <= 0 and current_stock <= 5:
            target_stock = 10

        recommended_restock_qty = max(target_stock - current_stock, 0)

        estimated_cost = recommended_restock_qty * to_float(variant.buy_price)
        estimated_sell_value = recommended_restock_qty * to_float(variant.sell_price)

        if recommended_restock_qty > 0:
            status = "Restock needed"
            reason = "Current stock is lower than the target stock."
            priority = 1
        elif current_stock <= 5:
            status = "Monitor closely"
            reason = "Stock is low, but recent sales speed does not require immediate restock."
            priority = 2
        else:
            status = "Enough stock"
            reason = "Current stock looks enough based on recent sales speed."
            priority = 3

        info = variant_label(db, variant)

        rows.append({
            "product_name": info["product_name"],
            "sku": info["sku"],
            "size": info["size"],
            "color": info["color"],
            "current_stock": current_stock,
            "sold_last_days": sold_qty,
            "avg_daily_sales_qty": round(avg_daily_sales_qty, 2),
            "target_stock": target_stock,
            "recommended_restock_qty": recommended_restock_qty,
            "estimated_buying_budget_bdt": money(estimated_cost),
            "estimated_selling_value_bdt": money(estimated_sell_value),
            "status": status,
            "reason": reason,
            "_priority": priority,
        })

    rows = sorted(
        rows,
        key=lambda item: (
            item["_priority"],
            -item["recommended_restock_qty"],
            item["current_stock"],
        )
    )

    for row in rows:
        row.pop("_priority", None)

    items_need_restock = len([row for row in rows if row["status"] == "Restock needed"])
    monitor_items = len([row for row in rows if row["status"] == "Monitor closely"])
    total_restock_qty = sum(row["recommended_restock_qty"] for row in rows)
    total_budget = sum(row["estimated_buying_budget_bdt"] for row in rows)

    if items_need_restock > 0:
        summary = f"{items_need_restock} item(s) need restock. Recommended total restock quantity is {total_restock_qty} piece(s). Estimated buying budget is {money(total_budget)} BDT."
    elif monitor_items > 0:
        summary = f"No immediate restock is required, but {monitor_items} item(s) should be monitored closely."
    else:
        summary = "No immediate restock is required. Current stock looks safe based on recent sales speed."

    return {
        "title": "Restock Plan",
        "summary": summary,
        "data": {
            "metrics": {
                "previous_sales_data_days": lookback_days,
                "lead_time_days": lead_time_days,
                "safety_days": safety_days,
                "items_need_restock": items_need_restock,
                "monitor_closely_items": monitor_items,
                "recommended_total_restock_qty": total_restock_qty,
                "estimated_total_buying_budget_bdt": money(total_budget),
            },
            "rows": rows[:50],
        },
    }


def customer_segments(db: Session):
    customers = db.query(Customer).order_by(Customer.id.desc()).all()
    orders = valid_orders(db)
    today = date.today()

    customer_stats = defaultdict(lambda: {
        "orders": 0,
        "total_spent": 0.0,
        "last_order_date": None,
    })

    for order in orders:
        stats = customer_stats[order.customer_id]
        stats["orders"] += 1
        stats["total_spent"] += to_float(order.final_amount)

        order_date = safe_date(order.created_at)

        if order_date:
            if stats["last_order_date"] is None or order_date > stats["last_order_date"]:
                stats["last_order_date"] = order_date

    rows = []
    segment_counts = defaultdict(int)

    for customer in customers:
        stats = customer_stats[customer.id]

        order_count = stats["orders"]
        total_spent = stats["total_spent"]
        last_order_date = stats["last_order_date"]

        if last_order_date:
            recency_days = (today - last_order_date).days
        else:
            recency_days = None

        segment = "No purchase yet"
        recommended_action = "First purchase offer"

        if order_count >= 5 and total_spent >= 10000:
            segment = "VIP customer"
            recommended_action = "Give exclusive offer"
        elif order_count >= 3:
            segment = "Loyal customer"
            recommended_action = "Give loyalty discount"
        elif recency_days is not None and recency_days <= 14:
            segment = "Recent buyer"
            recommended_action = "Recommend related products"
        elif recency_days is not None and recency_days >= 60:
            segment = "At-risk customer"
            recommended_action = "Send win-back offer"
        elif order_count >= 1:
            segment = "Regular customer"
            recommended_action = "Promote new arrivals"

        segment_counts[segment] += 1

        rows.append({
            "customer_id": customer.id,
            "name": customer.name,
            "phone": customer.phone,
            "email": customer.email or "",
            "segment": segment,
            "orders": order_count,
            "total_spent_bdt": money(total_spent),
            "recency_days": recency_days if recency_days is not None else "No purchase",
            "last_order_date": str(last_order_date) if last_order_date else "",
            "recommended_action": recommended_action,
        })

    rows = sorted(
        rows,
        key=lambda item: (
            item["segment"] != "VIP customer",
            item["segment"] != "Loyal customer",
            item["orders"] * -1,
        )
    )

    return {
        "title": "Customer Insights",
        "summary": f"{len(customers)} customer(s) analyzed using buying behavior, order count, spending amount and last purchase date.",
        "data": {
            "metrics": {
                "total_customers": len(customers),
                "vip_customers": segment_counts["VIP customer"],
                "loyal_customers": segment_counts["Loyal customer"],
                "recent_buyers": segment_counts["Recent buyer"],
                "regular_customers": segment_counts["Regular customer"],
                "at_risk_customers": segment_counts["At-risk customer"],
                "no_purchase_yet": segment_counts["No purchase yet"],
            },
            "rows": rows,
        },
    }


def product_recommendations(db: Session, customer_id: int | None = None, limit: int = 10):
    limit = max(1, min(int(limit), 20))

    valid_order_map = {
        order.id: order
        for order in valid_orders(db)
    }

    product_sales = defaultdict(lambda: {
        "quantity_sold": 0,
        "total_sales": 0.0,
    })

    customer_product_ids = set()
    customer_category_ids = set()

    order_items = db.query(OrderItem).all()

    for item in order_items:
        order = valid_order_map.get(item.order_id)

        if not order:
            continue

        variant = get_variant(db, item.variant_id)

        if not variant:
            continue

        product = get_product(db, variant.product_id)

        if not product:
            continue

        product_sales[product.id]["quantity_sold"] += item.quantity
        product_sales[product.id]["total_sales"] += to_float(item.total_price)

        if customer_id and order.customer_id == customer_id:
            customer_product_ids.add(product.id)

            if product.category_id:
                customer_category_ids.add(product.category_id)

    products = db.query(Product).all()
    rows = []

    for product in products:
        if not product_is_active(product):
            continue

        if customer_id and product.id in customer_product_ids:
            continue

        variants = db.query(ProductVariant).filter(ProductVariant.product_id == product.id).all()
        available_stock = sum(variant.stock_quantity or 0 for variant in variants)

        if available_stock <= 0:
            continue

        sales = product_sales[product.id]

        score = 0
        reasons = []

        if sales["quantity_sold"] > 0:
            score += sales["quantity_sold"] * 3
            reasons.append("popular product")

        if customer_id and product.category_id in customer_category_ids:
            score += 20
            reasons.append("same category as customer purchase history")

        if available_stock > 0:
            score += min(available_stock, 20)
            reasons.append("available in stock")

        if not reasons:
            reasons.append("active available product")

        rows.append({
            "product_id": product.id,
            "product_name": product.name,
            "category_id": product.category_id,
            "brand": product.brand or "",
            "available_stock": available_stock,
            "quantity_sold": sales["quantity_sold"],
            "total_sales_bdt": money(sales["total_sales"]),
            "recommendation_score": score,
            "reason": ", ".join(reasons),
        })

    rows = sorted(
        rows,
        key=lambda item: (
            -item["recommendation_score"],
            -item["available_stock"],
            item["product_name"],
        )
    )[:limit]

    if customer_id:
        customer = get_customer(db, customer_id)
        target_name = customer.name if customer else f"Customer {customer_id}"
        summary = f"Top {len(rows)} recommended product(s) for {target_name}."
    else:
        summary = f"Top {len(rows)} general product recommendation(s) based on sales popularity and available stock."

    return {
        "title": "Product Recommendations",
        "summary": summary,
        "data": {
            "metrics": {
                "recommendation_type": "customer based" if customer_id else "general",
                "customer_id": customer_id or "general",
                "recommended_products": len(rows),
            },
            "rows": rows,
        },
    }


def ml_summary(db: Session):
    products = db.query(Product).all()
    variants = db.query(ProductVariant).all()
    customers = db.query(Customer).all()
    orders = valid_orders(db)

    total_stock = sum(variant.stock_quantity or 0 for variant in variants)
    total_stock_value = sum(
        to_float(variant.sell_price) * (variant.stock_quantity or 0)
        for variant in variants
    )

    low_stock_result = low_stock_prediction(db, lookback_days=30)
    restock_result = reorder_recommendations(db, lookback_days=30)
    forecast_result = sales_forecast(db, forecast_days=7, lookback_days=30)
    customer_result = customer_segments(db)
    recommendation_result = product_recommendations(db, limit=10)

    low_metrics = low_stock_result["data"]["metrics"]
    restock_metrics = restock_result["data"]["metrics"]
    forecast_metrics = forecast_result["data"]["metrics"]
    customer_metrics = customer_result["data"]["metrics"]
    recommendation_metrics = recommendation_result["data"]["metrics"]

    return {
        "title": "Analytics Overview",
        "summary": "Your predictive analytics dashboard is ready. It analyzes sales forecast, stock risk, restock planning, customer insights and product recommendations.",
        "data": {
            "metrics": {
                "products": len(products),
                "variants": len(variants),
                "customers": len(customers),
                "valid_orders": len(orders),
                "total_stock": total_stock,
                "estimated_stock_selling_value_bdt": money(total_stock_value),
                "next_7_days_forecast_bdt": forecast_metrics["predicted_total_sales_bdt"],
                "stock_risk_items": low_metrics["total_flagged_items"],
                "items_need_restock": restock_metrics["items_need_restock"],
                "vip_customers": customer_metrics["vip_customers"],
                "recommended_products": recommendation_metrics["recommended_products"],
            },
            "modules": [
                "Sales Forecast",
                "Stock Risk Prediction",
                "Restock Plan",
                "Customer Insights",
                "Product Recommendations",
            ],
        },
    }
