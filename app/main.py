from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.dependencies.auth_dependency import require_admin, require_staff_or_admin

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
    description="Secure backend API for fashion store inventory, sales, orders, payments and reports.",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

staff_or_admin = [Depends(require_staff_or_admin)]
admin_only = [Depends(require_admin)]

# Public routes
app.include_router(auth.router)

# Admin-only routes
app.include_router(users.router, dependencies=admin_only)

# Logged-in staff/admin routes
app.include_router(categories.router, dependencies=staff_or_admin)
app.include_router(products.router, dependencies=staff_or_admin)
app.include_router(product_variants.router, dependencies=staff_or_admin)
app.include_router(stock_router.router, dependencies=staff_or_admin)
app.include_router(customers.router, dependencies=staff_or_admin)
app.include_router(orders.router, dependencies=staff_or_admin)
app.include_router(payments.router, dependencies=staff_or_admin)
app.include_router(invoices.router, dependencies=staff_or_admin)
app.include_router(reports.router, dependencies=staff_or_admin)

# Frontend
app.mount("/site", StaticFiles(directory="frontend", html=True), name="site")


@app.get("/")
def home():
    return {
        "message": "Fashion Store Inventory API is running successfully",
        "frontend": "http://127.0.0.1:8000/site/login.html",
        "dashboard": "http://127.0.0.1:8000/site/dashboard_v2.html",
        "docs": "http://127.0.0.1:8000/docs"
    }
