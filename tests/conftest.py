import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import (
    category,
    customer,
    invoice,
    order,
    payment,
    product,
    product_variant,
    stock,
    user,
)

TEST_DATABASE_URL = "sqlite:///./test_fashion_store.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def admin_token(client):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Admin User",
            "email": "admin@test.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200

    data = response.json()

    return data["access_token"]


@pytest.fixture(scope="function")
def admin_headers(admin_token):
    return {
        "Authorization": f"Bearer {admin_token}"
    }
