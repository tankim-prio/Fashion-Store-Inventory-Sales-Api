import random
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal, engine

try:
    from app.database import Base
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.payment import Payment

try:
    from app.utils.security import get_password_hash
except Exception:
    try:
        from app.utils.security import hash_password as get_password_hash
    except Exception:
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        def get_password_hash(password: str):
            return pwd_context.hash(password)


random.seed(42)


def has_column(model, column_name):
    return column_name in model.__table__.columns.keys()


def make_model(model, **kwargs):
    obj = model()

    for key, value in kwargs.items():
        if has_column(model, key):
            setattr(obj, key, value)

    return obj


def set_value(obj, key, value):
    if has_column(obj.__class__, key):
        setattr(obj, key, value)




def get_user_password_column():
    possible_columns = [
        "password_hash",
        "hashed_password",
        "password",
        "password_hashed",
    ]

    for column in possible_columns:
        if has_column(User, column):
            return column

    raise RuntimeError(
        "No password column found in User model. Expected one of: "
        "password_hash, hashed_password, password, password_hashed"
    )


def set_user_password(user, raw_password):
    password_column = get_user_password_column()
    setattr(user, password_column, get_password_hash(raw_password))


def get_or_create(db, model, defaults=None, **filters):
    obj = db.query(model).filter_by(**filters).first()

    if obj:
        return obj

    data = {}
    data.update(filters)
    data.update(defaults or {})

    obj = make_model(model, **data)

    db.add(obj)
    db.flush()

    return obj


def clean_previous_demo_orders(db):
    demo_orders = db.query(Order).filter(Order.order_number.like("DEMO-%")).all()
    demo_order_ids = [order.id for order in demo_orders]

    if demo_order_ids:
        db.query(Payment).filter(Payment.order_id.in_(demo_order_ids)).delete(synchronize_session=False)
        db.query(OrderItem).filter(OrderItem.order_id.in_(demo_order_ids)).delete(synchronize_session=False)
        db.query(Order).filter(Order.id.in_(demo_order_ids)).delete(synchronize_session=False)
        db.commit()

    print(f"Removed old demo orders: {len(demo_order_ids)}")


def seed_users(db):
    admin = db.query(User).filter(User.email == "admin.demo@gmail.com").first()

    if not admin:
        admin = make_model(
            User,
            full_name="Demo Admin",
            email="admin.demo@gmail.com",
            phone="01700000001",
            role="admin",
            is_active=True,
        )

        set_user_password(admin, "123456")
        db.add(admin)
    else:
        set_user_password(admin, "123456")
        set_value(admin, "role", "admin")
        set_value(admin, "is_active", True)

    staff = db.query(User).filter(User.email == "staff.demo@gmail.com").first()

    if not staff:
        staff = make_model(
            User,
            full_name="Demo Staff",
            email="staff.demo@gmail.com",
            phone="01700000002",
            role="staff",
            is_active=True,
        )

        set_user_password(staff, "123456")
        db.add(staff)
    else:
        set_user_password(staff, "123456")
        set_value(staff, "role", "staff")
        set_value(staff, "is_active", True)

    db.commit()

    print("Demo users ready")
    print("Admin: admin.demo@gmail.com / 123456")
    print("Staff: staff.demo@gmail.com / 123456")


def seed_categories(db):
    category_data = [
        ("T-Shirts", "Casual and premium cotton t-shirts"),
        ("Polo Shirts", "Smart casual polo collection"),
        ("Formal Shirts", "Office and formal shirt collection"),
        ("Jeans", "Men denim jeans collection"),
        ("Panjabi", "Traditional men panjabi collection"),
        ("Bottoms", "Joggers and trousers"),
        ("Accessories", "Wallet, belt and fashion accessories"),
        ("Footwear", "Sneakers and casual shoes"),
    ]

    categories = {}

    for name, description in category_data:
        category = get_or_create(
            db,
            Category,
            name=name,
            defaults={
                "description": description,
                "is_active": True,
            },
        )

        categories[name] = category

    db.commit()

    print(f"Categories ready: {len(categories)}")

    return categories


def seed_products_and_variants(db, categories):
    product_data = [
        {
            "name": "Classic Cotton T-Shirt",
            "category": "T-Shirts",
            "brand": "Anchor",
            "description": "Daily wear cotton t-shirt",
            "variants": [
                ("TS-BLK-M", "M", "Black", 180, 450, 8),
                ("TS-BLK-L", "L", "Black", 180, 450, 4),
                ("TS-WHT-M", "M", "White", 170, 430, 25),
                ("TS-NVY-XL", "XL", "Navy", 190, 470, 3),
            ],
        },
        {
            "name": "Premium Polo Shirt",
            "category": "Polo Shirts",
            "brand": "Anchor",
            "description": "Premium smart casual polo shirt",
            "variants": [
                ("POLO-GRN-M", "M", "Green", 420, 950, 6),
                ("POLO-NVY-L", "L", "Navy", 430, 990, 18),
                ("POLO-BLK-XL", "XL", "Black", 450, 1050, 2),
            ],
        },
        {
            "name": "Slim Fit Denim Jeans",
            "category": "Jeans",
            "brand": "Anchor",
            "description": "Slim fit stretch denim jeans",
            "variants": [
                ("JEANS-BLU-30", "30", "Blue", 850, 1890, 10),
                ("JEANS-BLU-32", "32", "Blue", 850, 1890, 5),
                ("JEANS-BLK-34", "34", "Black", 900, 1990, 2),
            ],
        },
        {
            "name": "Formal Office Shirt",
            "category": "Formal Shirts",
            "brand": "Anchor",
            "description": "Formal office shirt",
            "variants": [
                ("FS-WHT-M", "M", "White", 550, 1250, 14),
                ("FS-SKY-L", "L", "Sky Blue", 560, 1290, 7),
                ("FS-BLK-XL", "XL", "Black", 570, 1350, 3),
            ],
        },
        {
            "name": "Premium Panjabi",
            "category": "Panjabi",
            "brand": "Anchor",
            "description": "Premium festive panjabi",
            "variants": [
                ("PANJABI-WHT-M", "M", "White", 950, 2450, 9),
                ("PANJABI-MRN-L", "L", "Maroon", 980, 2550, 4),
                ("PANJABI-BLK-XL", "XL", "Black", 1000, 2650, 1),
            ],
        },
        {
            "name": "Casual Joggers",
            "category": "Bottoms",
            "brand": "Anchor",
            "description": "Comfortable casual joggers",
            "variants": [
                ("JOG-BLK-M", "M", "Black", 500, 1190, 16),
                ("JOG-GRY-L", "L", "Grey", 520, 1250, 6),
            ],
        },
        {
            "name": "Leather Belt",
            "category": "Accessories",
            "brand": "Anchor",
            "description": "Men premium leather belt",
            "variants": [
                ("BELT-BLK-FREE", "Free", "Black", 280, 790, 20),
                ("BELT-BRN-FREE", "Free", "Brown", 280, 790, 12),
            ],
        },
        {
            "name": "Casual Sneakers",
            "category": "Footwear",
            "brand": "Anchor",
            "description": "Stylish casual sneakers",
            "variants": [
                ("SNK-WHT-41", "41", "White", 1250, 2890, 8),
                ("SNK-BLK-42", "42", "Black", 1300, 2990, 5),
            ],
        },
    ]

    products = []
    variants = []

    for item in product_data:
        category = categories[item["category"]]

        product = get_or_create(
            db,
            Product,
            name=item["name"],
            defaults={
                "category_id": category.id,
                "brand": item["brand"],
                "description": item["description"],
                "is_active": True,
            },
        )

        set_value(product, "category_id", category.id)
        set_value(product, "brand", item["brand"])
        set_value(product, "description", item["description"])
        set_value(product, "is_active", True)

        products.append(product)

        for sku, size, color, buy_price, sell_price, stock_quantity in item["variants"]:
            variant = db.query(ProductVariant).filter(ProductVariant.sku == sku).first()

            if not variant:
                variant = make_model(
                    ProductVariant,
                    product_id=product.id,
                    sku=sku,
                    size=size,
                    color=color,
                    buy_price=Decimal(str(buy_price)),
                    sell_price=Decimal(str(sell_price)),
                    stock_quantity=stock_quantity,
                    is_active=True,
                )

                db.add(variant)
                db.flush()
            else:
                set_value(variant, "product_id", product.id)
                set_value(variant, "size", size)
                set_value(variant, "color", color)
                set_value(variant, "buy_price", Decimal(str(buy_price)))
                set_value(variant, "sell_price", Decimal(str(sell_price)))
                set_value(variant, "stock_quantity", stock_quantity)
                set_value(variant, "is_active", True)

            variants.append(variant)

    db.commit()

    print(f"Products ready: {len(products)}")
    print(f"Variants ready: {len(variants)}")

    return products, variants


def seed_customers(db):
    customer_data = [
        ("Rahim Ahmed", "01710000001", "rahim.demo@gmail.com", "Rangpur"),
        ("Karim Hasan", "01710000002", "karim.demo@gmail.com", "Dhaka"),
        ("Sabbir Hossain", "01710000003", "sabbir.demo@gmail.com", "Rangpur"),
        ("Nafis Rahman", "01710000004", "nafis.demo@gmail.com", "Dinajpur"),
        ("Tanvir Islam", "01710000005", "tanvir.demo@gmail.com", "Bogura"),
        ("Mehedi Hasan", "01710000006", "mehedi.demo@gmail.com", "Rajshahi"),
        ("Rafi Chowdhury", "01710000007", "rafi.demo@gmail.com", "Kurigram"),
        ("Arif Mahmud", "01710000008", "arif.demo@gmail.com", "Nilphamari"),
        ("Shuvo Khan", "01710000009", "shuvo.demo@gmail.com", "Gaibandha"),
        ("Hasibul Islam", "01710000010", "hasibul.demo@gmail.com", "Rangpur"),
        ("Imran Hossain", "01710000011", "imran.demo@gmail.com", "Lalmonirhat"),
        ("Sakib Rahman", "01710000012", "sakib.demo@gmail.com", "Dhaka"),
        ("Rasel Ahmed", "01710000013", "rasel.demo@gmail.com", "Rangpur"),
        ("Jahid Hasan", "01710000014", "jahid.demo@gmail.com", "Dinajpur"),
        ("Fahim Islam", "01710000015", "fahim.demo@gmail.com", "Bogura"),
        ("Noman Ali", "01710000016", "noman.demo@gmail.com", "Rajshahi"),
        ("Riyad Mahmud", "01710000017", "riyad.demo@gmail.com", "Rangpur"),
        ("Ashikur Rahman", "01710000018", "ashikur.demo@gmail.com", "Dhaka"),
        ("Mahin Khan", "01710000019", "mahin.demo@gmail.com", "Kurigram"),
        ("Rakib Hasan", "01710000020", "rakib.demo@gmail.com", "Nilphamari"),
    ]

    customers = []

    for name, phone, email, address in customer_data:
        customer = db.query(Customer).filter(Customer.phone == phone).first()

        if not customer:
            customer = make_model(
                Customer,
                name=name,
                phone=phone,
                email=email,
                address=address,
                is_active=True,
            )

            db.add(customer)
            db.flush()
        else:
            set_value(customer, "name", name)
            set_value(customer, "email", email)
            set_value(customer, "address", address)
            set_value(customer, "is_active", True)

        customers.append(customer)

    db.commit()

    print(f"Customers ready: {len(customers)}")

    return customers


def create_order(db, order_number, customer, items, status, created_at, discount=0, partial_payment=None):
    total_amount = sum(quantity * to_float(variant.sell_price) for variant, quantity in items)
    final_amount = max(total_amount - discount, 0)

    order = make_model(
        Order,
        order_number=order_number,
        customer_id=customer.id,
        total_amount=Decimal(str(total_amount)),
        discount=Decimal(str(discount)),
        final_amount=Decimal(str(final_amount)),
        status=status,
        created_by="seed_demo_data",
        created_at=created_at,
    )

    db.add(order)
    db.flush()

    for variant, quantity in items:
        unit_price = to_float(variant.sell_price)
        total_price = unit_price * quantity

        item = make_model(
            OrderItem,
            order_id=order.id,
            variant_id=variant.id,
            quantity=quantity,
            unit_price=Decimal(str(unit_price)),
            total_price=Decimal(str(total_price)),
        )

        db.add(item)

    if status == "paid":
        payment_amount = final_amount
        payment_status = "paid"
    elif partial_payment is not None:
        payment_amount = partial_payment
        payment_status = "paid"
    else:
        payment_amount = 0
        payment_status = "pending"

    if payment_amount > 0:
        payment = make_model(
            Payment,
            order_id=order.id,
            payment_method=random.choice(["cash", "bkash", "nagad", "card"]),
            amount=Decimal(str(payment_amount)),
            status=payment_status,
            transaction_id=f"TXN-{order_number}",
            paid_at=created_at,
            created_by="seed_demo_data",
        )

        db.add(payment)

    return order


def seed_orders_and_payments(db, customers, variants):
    clean_previous_demo_orders(db)

    today = datetime.now()
    paid_status_choices = ["paid"] * 8 + ["pending"] * 2

    popular_skus = [
        "TS-BLK-M",
        "TS-BLK-L",
        "POLO-BLK-XL",
        "JEANS-BLK-34",
        "PANJABI-BLK-XL",
        "FS-BLK-XL",
        "JOG-GRY-L",
    ]

    variant_by_sku = {
        variant.sku: variant
        for variant in variants
    }

    weighted_variants = []

    for variant in variants:
        weight = 4 if variant.sku in popular_skus else 1

        for _ in range(weight):
            weighted_variants.append(variant)

    order_count = 95

    for i in range(1, order_count + 1):
        days_ago = random.randint(0, 59)
        order_date = today - timedelta(
            days=days_ago,
            hours=random.randint(0, 8),
            minutes=random.randint(0, 59),
        )

        customer = random.choice(customers)

        item_count = random.choice([1, 1, 1, 2, 2, 3])
        selected_variants = random.sample(weighted_variants, item_count)

        order_items = []

        for variant in selected_variants:
            quantity = random.choice([1, 1, 1, 2, 2, 3])
            order_items.append((variant, quantity))

        status = random.choice(paid_status_choices)
        discount = random.choice([0, 0, 0, 50, 100, 150, 200])

        partial_payment = None

        if status == "pending":
            total_before_discount = sum(qty * to_float(v.sell_price) for v, qty in order_items)
            final_amount = max(total_before_discount - discount, 0)
            partial_payment = random.choice([0, round(final_amount * 0.3, 2), round(final_amount * 0.5, 2)])

        order_number = f"DEMO-{order_date.strftime('%Y%m%d')}-{i:04d}"

        create_order(
            db=db,
            order_number=order_number,
            customer=customer,
            items=order_items,
            status=status,
            created_at=order_date,
            discount=discount,
            partial_payment=partial_payment,
        )

    special_orders = [
        ("TS-BLK-L", 6),
        ("POLO-BLK-XL", 5),
        ("JEANS-BLK-34", 4),
        ("PANJABI-BLK-XL", 3),
        ("FS-BLK-XL", 4),
    ]

    for index, (sku, quantity) in enumerate(special_orders, start=1):
        variant = variant_by_sku.get(sku)

        if not variant:
            continue

        customer = customers[index % len(customers)]
        order_date = today - timedelta(days=random.randint(1, 10))
        order_number = f"DEMO-HOT-{index:04d}"

        create_order(
            db=db,
            order_number=order_number,
            customer=customer,
            items=[(variant, quantity)],
            status="paid",
            created_at=order_date,
            discount=0,
        )

    db.commit()

    print(f"Demo orders created: {order_count + len(special_orders)}")
    print("Payments created for paid and partial due orders")


def seed_demo_data():
    db = SessionLocal()

    try:
        print("Starting demo seed data...")

        seed_users(db)
        categories = seed_categories(db)
        products, variants = seed_products_and_variants(db, categories)
        customers = seed_customers(db)
        seed_orders_and_payments(db, customers, variants)

        db.commit()

        print("")
        print("Demo seed data completed successfully.")
        print("")
        print("Login credentials:")
        print("Admin: admin.demo@gmail.com / 123456")
        print("Staff: staff.demo@gmail.com / 123456")
        print("")
        print("Now test:")
        print("1. AI Assistant")
        print("2. Predictive Analytics")
        print("3. Sales Forecast")
        print("4. Stock Risk Prediction")
        print("5. Restock Plan")
        print("6. Customer Insights")
        print("7. Product Recommendations")

    except IntegrityError as error:
        db.rollback()
        print("Database integrity error:")
        print(error)

    except Exception as error:
        db.rollback()
        print("Seed failed:")
        print(error)

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
