from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth_dependency import require_staff_or_admin
from app.models.user import User
from app.schemas.ml import MLResponse
from app.services.ml_service import (
    customer_segments,
    low_stock_prediction,
    ml_summary,
    product_recommendations,
    reorder_recommendations,
    sales_forecast,
)

router = APIRouter(prefix="/ml", tags=["Predictive Analytics"])


@router.get("/summary", response_model=MLResponse)
def get_ml_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
):
    return ml_summary(db)


@router.get("/sales-forecast", response_model=MLResponse)
def get_sales_forecast(
    days: int = Query(default=7, ge=1, le=30),
    lookback_days: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
):
    return sales_forecast(
        db=db,
        forecast_days=days,
        lookback_days=lookback_days,
    )


@router.get("/low-stock-prediction", response_model=MLResponse)
def get_low_stock_prediction(
    lookback_days: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
):
    return low_stock_prediction(
        db=db,
        lookback_days=lookback_days,
    )


@router.get("/reorder-recommendations", response_model=MLResponse)
def get_reorder_recommendations(
    lookback_days: int = Query(default=30, ge=1, le=90),
    lead_time_days: int = Query(default=7, ge=1, le=60),
    safety_days: int = Query(default=5, ge=1, le=60),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
):
    return reorder_recommendations(
        db=db,
        lookback_days=lookback_days,
        lead_time_days=lead_time_days,
        safety_days=safety_days,
    )


@router.get("/customer-segments", response_model=MLResponse)
def get_customer_segments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
):
    return customer_segments(db)


@router.get("/product-recommendations", response_model=MLResponse)
def get_general_product_recommendations(
    limit: int = Query(default=10, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
):
    return product_recommendations(
        db=db,
        customer_id=None,
        limit=limit,
    )


@router.get("/product-recommendations/{customer_id}", response_model=MLResponse)
def get_customer_product_recommendations(
    customer_id: int,
    limit: int = Query(default=10, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
):
    return product_recommendations(
        db=db,
        customer_id=customer_id,
        limit=limit,
    )
