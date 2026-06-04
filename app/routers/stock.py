from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product_variant import ProductVariant
from app.models.stock import StockHistory
from app.schemas.stock import (
    LowStockResponse,
    StockAdd,
    StockHistoryResponse,
    StockRemove,
)
from app.services.stock_service import add_stock, remove_stock

router = APIRouter(
    prefix="/stock",
    tags=["Stock Management"]
)


@router.post("/add", response_model=StockHistoryResponse)
def add_stock_route(stock: StockAdd, db: Session = Depends(get_db)):
    return add_stock(
        db=db,
        variant_id=stock.variant_id,
        quantity=stock.quantity,
        note=stock.note,
        created_by=stock.created_by
    )


@router.post("/remove", response_model=StockHistoryResponse)
def remove_stock_route(stock: StockRemove, db: Session = Depends(get_db)):
    return remove_stock(
        db=db,
        variant_id=stock.variant_id,
        quantity=stock.quantity,
        note=stock.note,
        created_by=stock.created_by
    )


@router.get("/history", response_model=list[StockHistoryResponse])
def get_stock_history(
    variant_id: Optional[int] = None,
    change_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(StockHistory)

    if variant_id:
        query = query.filter(StockHistory.variant_id == variant_id)

    if change_type:
        query = query.filter(StockHistory.change_type == change_type)

    return query.order_by(StockHistory.id.desc()).all()


@router.get("/low", response_model=list[LowStockResponse])
def get_low_stock(
    threshold: int = 5,
    db: Session = Depends(get_db)
):
    variants = db.query(ProductVariant).filter(
        ProductVariant.is_active.is_(True),
        ProductVariant.stock_quantity <= threshold
    ).all()

    return variants
