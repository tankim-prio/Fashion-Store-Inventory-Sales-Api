from fastapi import FastAPI

from app.database import Base, engine
from app.models import category, product, product_variant, stock
from app.routers import categories, product_variants, products, stock as stock_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fashion Store Inventory API",
    description="Backend API for fashion store inventory, sales, orders, payments and reports.",
    version="1.0.0"
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(product_variants.router)
app.include_router(stock_router.router)


@app.get("/")
def home():
    return {
        "message": "Fashion Store Inventory API is running successfully"
    }
