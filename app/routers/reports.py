from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth_dependency import require_admin
from app.models.user import User
from app.schemas.report import (
    LowStockReportResponse,
    ProfitReportResponse,
    SalesReportResponse,
    TopProductResponse,
)
from app.services.report_service import (
    get_daily_sales_report,
    get_low_stock_report,
    get_monthly_sales_report,
    get_profit_report,
    get_top_products_report,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/daily-sales", response_model=SalesReportResponse)
def daily_sales_report(
    report_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return get_daily_sales_report(db=db, report_date=report_date)


@router.get("/monthly-sales", response_model=SalesReportResponse)
def monthly_sales_report(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return get_monthly_sales_report(db=db, year=year, month=month)


@router.get("/top-products", response_model=list[TopProductResponse])
def top_products_report(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return get_top_products_report(db=db, limit=limit)


@router.get("/profit", response_model=ProfitReportResponse)
def profit_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return get_profit_report(db=db)


@router.get("/low-stock", response_model=list[LowStockReportResponse])
def low_stock_report(
    threshold: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return get_low_stock_report(db=db, threshold=threshold)
