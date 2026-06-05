def test_register_first_user_as_admin(client):
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

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@test.com"
    assert data["user"]["role"] == "admin"


def test_public_register_disabled_after_first_user(client):
    client.post(
        "/auth/register",
        json={
            "full_name": "Admin User",
            "email": "admin@test.com",
            "password": "123456"
        }
    )

    response = client.post(
        "/auth/register",
        json={
            "full_name": "Second User",
            "email": "second@test.com",
            "password": "123456"
        }
    )

    assert response.status_code == 403
    assert response.json()["success"] is False


def test_login_success(client):
    client.post(
        "/auth/register",
        json={
            "full_name": "Admin User",
            "email": "admin@test.com",
            "password": "123456"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "admin@test.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["user"]["email"] == "admin@test.com"


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "full_name": "Admin User",
            "email": "admin@test.com",
            "password": "123456"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "admin@test.com",
            "password": "wrongpass"
        }
    )

    assert response.status_code == 401
    assert response.json()["success"] is False


def test_protected_route_without_token_blocked(client):
    response = client.get("/products/")

    assert response.status_code == 401
    assert response.json()["success"] is False
