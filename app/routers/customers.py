from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth_dependency import require_staff_or_admin
from app.models.user import User
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.post("/", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    existing_phone = db.query(Customer).filter(
        Customer.phone == customer.phone
    ).first()

    if existing_phone:
        raise HTTPException(
            status_code=400,
            detail="Customer with this phone already exists"
        )

    if customer.email:
        existing_email = db.query(Customer).filter(
            Customer.email == customer.email
        ).first()

        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Customer with this email already exists"
            )

    new_customer = Customer(**customer.model_dump())

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


@router.get("/", response_model=list[CustomerResponse])
def get_customers(
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Customer).filter(Customer.is_active.is_(True))

    if search:
        query = query.filter(
            (Customer.name.ilike(f"%{search}%")) |
            (Customer.phone.ilike(f"%{search}%")) |
            (Customer.email.ilike(f"%{search}%"))
        )

    return query.all()


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.is_active.is_(True)
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.is_active.is_(True)
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    update_data = customer_data.model_dump(exclude_unset=True)

    if "phone" in update_data:
        existing_phone = db.query(Customer).filter(
            Customer.phone == update_data["phone"],
            Customer.id != customer_id
        ).first()

        if existing_phone:
            raise HTTPException(
                status_code=400,
                detail="Customer with this phone already exists"
            )

    if "email" in update_data and update_data["email"]:
        existing_email = db.query(Customer).filter(
            Customer.email == update_data["email"],
            Customer.id != customer_id
        ).first()

        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Customer with this email already exists"
            )

    for key, value in update_data.items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)

    return customer


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.is_active.is_(True)
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    customer.is_active = False

    db.commit()

    return {"message": "Customer deleted successfully"}
