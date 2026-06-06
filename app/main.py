from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    ai_assistant,
    ml,
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
    description="Secure backend API for fashion store inventory, sales, orders, payments, reports and AI assistant.",
    version="1.4.0"
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"

    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "success": False,
            "message": message,
            "errors": exc.detail if not isinstance(exc.detail, str) else None
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []

    for error in exc.errors():
        location = error.get("loc", [])
        field_parts = [str(item) for item in location if item != "body"]
        field = ".".join(field_parts) if field_parts else "request"
        message = error.get("msg", "Invalid value")

        formatted_errors.append({
            "field": field,
            "message": message,
            "type": error.get("type", "validation_error")
        })

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation failed",
            "errors": formatted_errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "errors": [
                {
                    "field": "server",
                    "message": "Something went wrong. Check terminal logs for details."
                }
            ]
        }
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

app.include_router(auth.router)

app.include_router(users.router, dependencies=admin_only)

app.include_router(categories.router, dependencies=staff_or_admin)
app.include_router(products.router, dependencies=staff_or_admin)
app.include_router(product_variants.router, dependencies=staff_or_admin)
app.include_router(stock_router.router, dependencies=staff_or_admin)
app.include_router(customers.router, dependencies=staff_or_admin)
app.include_router(orders.router, dependencies=staff_or_admin)
app.include_router(payments.router, dependencies=staff_or_admin)
app.include_router(invoices.router, dependencies=staff_or_admin)
app.include_router(reports.router, dependencies=staff_or_admin)
app.include_router(ai_assistant.router, dependencies=staff_or_admin)
app.include_router(ml.router, dependencies=staff_or_admin)

app.mount("/site", StaticFiles(directory="frontend", html=True), name="site")


@app.get("/")
def home():
    return {
        "success": True,
        "message": "Fashion Store Inventory API is running successfully",
        "frontend": "http://127.0.0.1:8000/site/login.html",
        "dashboard": "http://127.0.0.1:8000/site/dashboard_v2.html",
        "docs": "http://127.0.0.1:8000/docs"
    }
