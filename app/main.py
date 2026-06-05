from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.models import (
    category,
    customer,
    invoice,
    order,
    payment,
    product,
    product_variant,
    stock,
    user,
)
from app.routers import (
    auth,
    categories,
    customers,
    invoices,
    orders,
    payments,
    product_variants,
    products,
    reports,
    stock as stock_router,
    users,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fashion Store Inventory API",
    description="Backend API for fashion store inventory, sales, orders, payments and reports.",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(users.router)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(product_variants.router)
app.include_router(stock_router.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(invoices.router)
app.include_router(reports.router)

app.mount("/site", StaticFiles(directory="frontend", html=True), name="site")


@app.get("/")
def home():
    return {
        "message": "Fashion Store Inventory API is running successfully",
        "frontend": "http://127.0.0.1:8000/site/login.html",
        "docs": "http://127.0.0.1:8000/docs"
    }
