def test_create_category(client, admin_headers):
    response = client.post(
        "/categories/",
        json={
            "name": "Shirt",
            "description": "Men shirt collection"
        },
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Shirt"
    assert data["description"] == "Men shirt collection"


def test_get_categories(client, admin_headers):
    client.post(
        "/categories/",
        json={
            "name": "Panjabi",
            "description": "Panjabi collection"
        },
        headers=admin_headers
    )

    response = client.get("/categories/", headers=admin_headers)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Panjabi"


def test_create_product(client, admin_headers):
    category_response = client.post(
        "/categories/",
        json={
            "name": "T-Shirt",
            "description": "T-shirt collection"
        },
        headers=admin_headers
    )

    category_id = category_response.json()["id"]

    response = client.post(
        "/products/",
        json={
            "name": "Black Cotton T-Shirt",
            "category_id": category_id,
            "brand": "Anchor",
            "description": "Premium cotton t-shirt"
        },
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Black Cotton T-Shirt"
    assert data["category_id"] == category_id
    assert data["is_active"] is True


def test_product_validation_empty_name(client, admin_headers):
    response = client.post(
        "/products/",
        json={
            "name": "",
            "category_id": 1,
            "brand": "Anchor",
            "description": "Bad product"
        },
        headers=admin_headers
    )

    assert response.status_code == 422
    assert response.json()["success"] is False
