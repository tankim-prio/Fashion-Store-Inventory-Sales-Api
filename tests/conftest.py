import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.user import User

try:
    from app.utils.security import get_password_hash
except Exception:
    from app.utils.security import hash_password as get_password_hash


TEST_ADMIN_EMAIL = "admin.demo@gmail.com"
TEST_ADMIN_PASSWORD = "123456"


def model_has_column(model, column_name):
    return column_name in model.__table__.columns.keys()


def set_if_exists(obj, field_name, value):
    if model_has_column(obj.__class__, field_name):
        setattr(obj, field_name, value)


def get_password_column_name():
    possible_columns = [
        "password_hash",
        "hashed_password",
        "password",
        "password_hashed",
    ]

    for column in possible_columns:
        if model_has_column(User, column):
            return column

    raise RuntimeError(
        "No password column found in User model. Expected one of: "
        "password_hash, hashed_password, password, password_hashed"
    )


def ensure_test_admin_user():
    db = SessionLocal()

    try:
        password_column = get_password_column_name()
        hashed_password = get_password_hash(TEST_ADMIN_PASSWORD)

        user = db.query(User).filter(User.email == TEST_ADMIN_EMAIL).first()

        if not user:
            user = User()
            db.add(user)

        set_if_exists(user, "full_name", "Demo Admin")
        set_if_exists(user, "name", "Demo Admin")
        set_if_exists(user, "email", TEST_ADMIN_EMAIL)
        set_if_exists(user, "phone", "01700000001")
        set_if_exists(user, "role", "admin")
        set_if_exists(user, "is_active", True)

        setattr(user, password_column, hashed_password)

        db.commit()
        db.refresh(user)

    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides.clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def admin_headers(client):
    ensure_test_admin_user()

    response = client.post(
        "/auth/login",
        data={
            "username": TEST_ADMIN_EMAIL,
            "password": TEST_ADMIN_PASSWORD,
        },
    )

    assert response.status_code == 200, response.text

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }
