from uuid import uuid4


def unique_suffix():
    return uuid4().hex[:8]


def unique_phone(prefix="018"):
    digits = str(uuid4().int)[:8]
    return f"{prefix}{digits}"


def test_create_customer(client, admin_headers):
    suffix = unique_suffix()
    phone = unique_phone("018")

    response = client.post(
        "/customers/",
        json={
            "name": f"Test Customer {suffix}",
            "phone": phone,
            "email": f"customer{suffix}@test.com",
            "address": "Dhaka",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["name"] == f"Test Customer {suffix}"
    assert data["phone"] == phone
    assert data["email"] == f"customer{suffix}@test.com"


def test_invalid_customer_phone(client, admin_headers):
    suffix = unique_suffix()

    response = client.post(
        "/customers/",
        json={
            "name": f"Invalid Customer {suffix}",
            "phone": "abc",
            "email": f"invalid{suffix}@test.com",
            "address": "Dhaka",
        },
        headers=admin_headers,
    )

    assert response.status_code in [400, 422], response.text


def test_get_customers(client, admin_headers):
    suffix = unique_suffix()
    phone = unique_phone("019")

    create_response = client.post(
        "/customers/",
        json={
            "name": f"Karim Uddin {suffix}",
            "phone": phone,
            "email": f"karim{suffix}@test.com",
            "address": "Dhaka",
        },
        headers=admin_headers,
    )

    assert create_response.status_code == 200, create_response.text

    created_customer = create_response.json()

    response = client.get("/customers/", headers=admin_headers)

    assert response.status_code == 200, response.text

    data = response.json()

    assert isinstance(data, list)
    assert any(customer["id"] == created_customer["id"] for customer in data)
