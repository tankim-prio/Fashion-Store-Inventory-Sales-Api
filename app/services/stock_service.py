from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.product_variant import ProductVariant
from app.models.stock import StockHistory


def add_stock(
    db: Session,
    variant_id: int,
    quantity: int,
    note: str | None = None,
    created_by: str | None = None
):
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    variant = db.query(ProductVariant).filter(
        ProductVariant.id == variant_id,
        ProductVariant.is_active.is_(True)
    ).first()

    if not variant:
        raise HTTPException(
            status_code=404,
            detail="Variant not found"
        )

    previous_stock = variant.stock_quantity
    new_stock = previous_stock + quantity

    variant.stock_quantity = new_stock

    stock_history = StockHistory(
        variant_id=variant_id,
        change_type="stock_in",
        quantity=quantity,
        previous_stock=previous_stock,
        new_stock=new_stock,
        note=note,
        created_by=created_by
    )

    db.add(stock_history)
    db.commit()
    db.refresh(stock_history)

    return stock_history


def remove_stock(
    db: Session,
    variant_id: int,
    quantity: int,
    note: str | None = None,
    created_by: str | None = None
):
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    variant = db.query(ProductVariant).filter(
        ProductVariant.id == variant_id,
        ProductVariant.is_active.is_(True)
    ).first()

    if not variant:
        raise HTTPException(
            status_code=404,
            detail="Variant not found"
        )

    if variant.stock_quantity < quantity:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock available"
        )

    previous_stock = variant.stock_quantity
    new_stock = previous_stock - quantity

    variant.stock_quantity = new_stock

    stock_history = StockHistory(
        variant_id=variant_id,
        change_type="stock_out",
        quantity=quantity,
        previous_stock=previous_stock,
        new_stock=new_stock,
        note=note,
        created_by=created_by
    )

    db.add(stock_history)
    db.commit()
    db.refresh(stock_history)

    return stock_history
