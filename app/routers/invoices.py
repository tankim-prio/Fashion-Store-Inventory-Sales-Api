from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceListResponse, InvoiceResponse
from app.services.invoice_service import get_invoice_by_id, get_or_create_invoice

router = APIRouter(
    tags=["Invoices"]
)


@router.get("/orders/{order_id}/invoice", response_model=InvoiceResponse)
def get_order_invoice(order_id: int, db: Session = Depends(get_db)):
    return get_or_create_invoice(db=db, order_id=order_id)


@router.get("/invoices/", response_model=list[InvoiceListResponse])
def get_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).order_by(Invoice.id.desc()).all()
    return invoices


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    return get_invoice_by_id(db=db, invoice_id=invoice_id)
