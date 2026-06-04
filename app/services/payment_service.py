from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment


ALLOWED_PAYMENT_METHODS = ["cash", "bkash", "nagad", "card"]
ALLOWED_PAYMENT_STATUSES = ["pending", "paid", "failed", "refunded"]


def create_payment(db: Session, payment_data):
    if payment_data.payment_method not in ALLOWED_PAYMENT_METHODS:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment method"
        )

    if payment_data.status not in ALLOWED_PAYMENT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment status"
        )

    if payment_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Payment amount must be greater than zero"
        )

    order = db.query(Order).filter(Order.id == payment_data.order_id).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.status in ["cancelled", "refunded"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot make payment for cancelled or refunded order"
        )

    if payment_data.transaction_id:
        existing_transaction = db.query(Payment).filter(
            Payment.transaction_id == payment_data.transaction_id
        ).first()

        if existing_transaction:
            raise HTTPException(
                status_code=400,
                detail="Transaction ID already exists"
            )

    paid_amount = db.query(Payment).filter(
        Payment.order_id == order.id,
        Payment.status == "paid"
    ).all()

    total_paid = sum(payment.amount for payment in paid_amount)

    if payment_data.status == "paid":
        remaining_amount = order.final_amount - total_paid

        if payment_data.amount > remaining_amount:
            raise HTTPException(
                status_code=400,
                detail="Payment amount is greater than remaining order amount"
            )

    new_payment = Payment(
        order_id=payment_data.order_id,
        payment_method=payment_data.payment_method,
        amount=payment_data.amount,
        status=payment_data.status,
        transaction_id=payment_data.transaction_id,
        paid_at=datetime.now() if payment_data.status == "paid" else None
    )

    db.add(new_payment)
    db.flush()

    if payment_data.status == "paid":
        new_total_paid = total_paid + payment_data.amount

        if new_total_paid >= order.final_amount:
            order.status = "paid"

    db.commit()
    db.refresh(new_payment)

    return new_payment


def update_payment_status(db: Session, payment_id: int, status: str, transaction_id: str | None = None):
    if status not in ALLOWED_PAYMENT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment status"
        )

    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    if transaction_id:
        existing_transaction = db.query(Payment).filter(
            Payment.transaction_id == transaction_id,
            Payment.id != payment_id
        ).first()

        if existing_transaction:
            raise HTTPException(
                status_code=400,
                detail="Transaction ID already exists"
            )

        payment.transaction_id = transaction_id

    payment.status = status
    payment.paid_at = datetime.now() if status == "paid" else payment.paid_at

    db.commit()
    db.refresh(payment)

    return payment
