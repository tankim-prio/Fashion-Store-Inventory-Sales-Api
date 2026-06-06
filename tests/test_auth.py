def test_login_success(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "admin.demo@gmail.com",
            "password": "123456",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "admin.demo@gmail.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_public_register_disabled_after_existing_user(client):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "New Public User",
            "email": "new.public.user@test.com",
            "password": "123456",
            "phone": "01799999999",
        },
    )

    assert response.status_code in [400, 403]


def test_protected_route_without_token_blocked(client):
    response = client.get("/products/")

    assert response.status_code in [401, 403]


def test_protected_route_with_token_allowed(client, admin_headers):
    response = client.get("/products/", headers=admin_headers)

    assert response.status_code == 200
