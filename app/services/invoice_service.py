from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.models.order import Order
from app.models.payment import Payment


def generate_invoice_number():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"INV-{timestamp}"


def calculate_payment_status(db: Session, order: Order):
    paid_payments = db.query(Payment).filter(
        Payment.order_id == order.id,
        Payment.status == "paid"
    ).all()

    paid_amount = sum(payment.amount for payment in paid_payments)
    due_amount = order.final_amount - paid_amount

    if paid_amount >= order.final_amount:
        payment_status = "paid"
        due_amount = 0
    elif paid_amount > 0:
        payment_status = "partial"
    else:
        payment_status = "unpaid"

    return paid_amount, due_amount, payment_status


def build_invoice_response(db: Session, invoice: Invoice, order: Order):
    paid_amount, due_amount, payment_status = calculate_payment_status(db, order)

    invoice_items = []

    for item in order.items:
        variant = item.variant
        product = variant.product if variant else None

        invoice_items.append({
            "variant_id": item.variant_id,
            "product_name": product.name if product else None,
            "size": variant.size if variant else "",
            "color": variant.color if variant else "",
            "sku": variant.sku if variant else "",
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.total_price
        })

    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,

        "order_id": order.id,
        "order_number": order.order_number,
        "order_status": order.status,

        "customer_id": order.customer_id,
        "customer_name": order.customer.name if order.customer else None,
        "customer_phone": order.customer.phone if order.customer else None,

        "items": invoice_items,

        "total_amount": order.total_amount,
        "discount": order.discount,
        "final_amount": order.final_amount,

        "paid_amount": paid_amount,
        "due_amount": due_amount,
        "payment_status": payment_status,

        "created_at": invoice.created_at
    }


def get_or_create_invoice(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if not order.items:
        raise HTTPException(
            status_code=400,
            detail="Order has no items"
        )

    invoice = db.query(Invoice).filter(
        Invoice.order_id == order.id
    ).first()

    if not invoice:
        invoice = Invoice(
            order_id=order.id,
            invoice_number=generate_invoice_number()
        )

        db.add(invoice)
        db.commit()
        db.refresh(invoice)

    return build_invoice_response(db=db, invoice=invoice, order=order)


def get_invoice_by_id(db: Session, invoice_id: int):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    return build_invoice_response(
        db=db,
        invoice=invoice,
        order=invoice.order
    )
