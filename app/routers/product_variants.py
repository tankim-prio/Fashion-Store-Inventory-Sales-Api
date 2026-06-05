from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth_dependency import require_admin, require_staff_or_admin
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.user import User
from app.schemas.product_variant import (
    ProductVariantCreate,
    ProductVariantResponse,
    ProductVariantUpdate,
)

router = APIRouter(
    prefix="/variants",
    tags=["Product Variants"]
)


@router.post("/", response_model=ProductVariantResponse)
def create_variant(
    variant: ProductVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    product = db.query(Product).filter(
        Product.id == variant.product_id,
        Product.is_active.is_(True)
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_sku = db.query(ProductVariant).filter(
        ProductVariant.sku == variant.sku
    ).first()

    if existing_sku:
        raise HTTPException(status_code=400, detail="SKU already exists")

    if variant.buy_price < 0 or variant.sell_price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")

    if variant.sell_price < variant.buy_price:
        raise HTTPException(
            status_code=400,
            detail="Sell price cannot be lower than buy price"
        )

    if variant.stock_quantity < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock quantity cannot be negative"
        )

    new_variant = ProductVariant(**variant.model_dump())

    db.add(new_variant)
    db.commit()
    db.refresh(new_variant)

    return new_variant


@router.get("/", response_model=list[ProductVariantResponse])
def get_variants(
    product_id: Optional[int] = None,
    size: Optional[str] = None,
    color: Optional[str] = None,
    only_in_stock: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    query = db.query(ProductVariant).filter(ProductVariant.is_active.is_(True))

    if product_id:
        query = query.filter(ProductVariant.product_id == product_id)

    if size:
        query = query.filter(ProductVariant.size.ilike(f"%{size}%"))

    if color:
        query = query.filter(ProductVariant.color.ilike(f"%{color}%"))

    if only_in_stock:
        query = query.filter(ProductVariant.stock_quantity > 0)

    return query.all()


@router.get("/{variant_id}", response_model=ProductVariantResponse)
def get_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    variant = db.query(ProductVariant).filter(
        ProductVariant.id == variant_id,
        ProductVariant.is_active.is_(True)
    ).first()

    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    return variant


@router.put("/{variant_id}", response_model=ProductVariantResponse)
def update_variant(
    variant_id: int,
    variant_data: ProductVariantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    variant = db.query(ProductVariant).filter(
        ProductVariant.id == variant_id,
        ProductVariant.is_active.is_(True)
    ).first()

    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    update_data = variant_data.model_dump(exclude_unset=True)

    if "product_id" in update_data:
        product = db.query(Product).filter(
            Product.id == update_data["product_id"],
            Product.is_active.is_(True)
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

    if "sku" in update_data:
        existing_sku = db.query(ProductVariant).filter(
            ProductVariant.sku == update_data["sku"],
            ProductVariant.id != variant_id
        ).first()

        if existing_sku:
            raise HTTPException(status_code=400, detail="SKU already exists")

    new_buy_price = update_data.get("buy_price", variant.buy_price)
    new_sell_price = update_data.get("sell_price", variant.sell_price)
    new_stock_quantity = update_data.get("stock_quantity", variant.stock_quantity)

    if new_buy_price < 0 or new_sell_price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")

    if new_sell_price < new_buy_price:
        raise HTTPException(
            status_code=400,
            detail="Sell price cannot be lower than buy price"
        )

    if new_stock_quantity < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock quantity cannot be negative"
        )

    for key, value in update_data.items():
        setattr(variant, key, value)

    db.commit()
    db.refresh(variant)

    return variant


@router.delete("/{variant_id}")
def delete_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    variant = db.query(ProductVariant).filter(
        ProductVariant.id == variant_id,
        ProductVariant.is_active.is_(True)
    ).first()

    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    variant.is_active = False
    db.commit()

    return {"message": "Variant deleted successfully"}
