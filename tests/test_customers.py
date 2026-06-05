def test_create_customer(client, admin_headers):
    response = client.post(
        "/customers/",
        json={
            "name": "Rahim Uddin",
            "phone": "01711111111",
            "email": "rahim@test.com",
            "address": "Rangpur"
        },
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Rahim Uddin"
    assert data["phone"] == "01711111111"
    assert data["email"] == "rahim@test.com"


def test_invalid_customer_phone(client, admin_headers):
    response = client.post(
        "/customers/",
        json={
            "name": "Bad Customer",
            "phone": "abc123",
            "email": "bad@test.com",
            "address": "Rangpur"
        },
        headers=admin_headers
    )

    assert response.status_code == 422
    assert response.json()["success"] is False


def test_get_customers(client, admin_headers):
    client.post(
        "/customers/",
        json={
            "name": "Karim Uddin",
            "phone": "01811111111",
            "email": "karim@test.com",
            "address": "Dhaka"
        },
        headers=admin_headers
    )

    response = client.get("/customers/", headers=admin_headers)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
