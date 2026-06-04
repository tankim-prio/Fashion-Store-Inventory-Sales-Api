from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate
from app.services.payment_service import create_payment, update_payment_status

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post("/", response_model=PaymentResponse)
def create_payment_route(payment: PaymentCreate, db: Session = Depends(get_db)):
    return create_payment(db=db, payment_data=payment)


@router.get("/", response_model=list[PaymentResponse])
def get_payments(
    order_id: Optional[int] = None,
    status: Optional[str] = None,
    payment_method: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Payment)

    if order_id:
        query = query.filter(Payment.order_id == order_id)

    if status:
        query = query.filter(Payment.status == status)

    if payment_method:
        query = query.filter(Payment.payment_method == payment_method)

    return query.order_by(Payment.id.desc()).all()


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    return payment


@router.put("/{payment_id}/status", response_model=PaymentResponse)
def update_payment_status_route(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db)
):
    return update_payment_status(
        db=db,
        payment_id=payment_id,
        status=payment_data.status,
        transaction_id=payment_data.transaction_id
    )


@router.get("/order/{order_id}", response_model=list[PaymentResponse])
def get_order_payments(order_id: int, db: Session = Depends(get_db)):
    payments = db.query(Payment).filter(
        Payment.order_id == order_id
    ).order_by(Payment.id.desc()).all()

    return payments
