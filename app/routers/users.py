from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.dependencies.auth_dependency import require_admin
from app.services.auth_service import (
    create_user_by_admin,
    update_user_by_admin,
    deactivate_user_by_admin,
)

router = APIRouter(prefix="/users", tags=["Users"])


def serialize_user(user: User):
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": str(user.created_at) if getattr(user, "created_at", None) else None
    }


@router.post("/")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    new_user = create_user_by_admin(db=db, user_data=user)
    return serialize_user(new_user)


@router.get("/")
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    users = db.query(User).order_by(User.id.desc()).all()
    return [serialize_user(user) for user in users]


@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return serialize_user(user)


@router.put("/{user_id}")
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    updated_user = update_user_by_admin(db=db, user_id=user_id, user_data=user)
    return serialize_user(updated_user)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own account"
        )

    return deactivate_user_by_admin(db=db, user_id=user_id)
