from uuid import uuid4


def unique_text(prefix):
    return f"{prefix}-{uuid4().hex[:8]}"


def create_test_category(client, admin_headers):
    name = unique_text("Test Category")

    response = client.post(
        "/categories/",
        json={
            "name": name,
            "description": "Test category description",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text

    return response.json()


def test_create_category(client, admin_headers):
    name = unique_text("Test Shirt")

    response = client.post(
        "/categories/",
        json={
            "name": name,
            "description": "Men shirt collection",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["name"] == name
    assert data["description"] == "Men shirt collection"


def test_get_categories(client, admin_headers):
    category = create_test_category(client, admin_headers)

    response = client.get("/categories/", headers=admin_headers)

    assert response.status_code == 200, response.text

    data = response.json()

    assert isinstance(data, list)
    assert any(item["id"] == category["id"] for item in data)


def test_create_product(client, admin_headers):
    category = create_test_category(client, admin_headers)

    product_name = unique_text("Test Product")

    response = client.post(
        "/products/",
        json={
            "name": product_name,
            "description": "Test product description",
            "brand": "Test Brand",
            "category_id": category["id"],
        },
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["name"] == product_name
    assert data["category_id"] == category["id"]


def test_product_validation_empty_name(client, admin_headers):
    category = create_test_category(client, admin_headers)

    response = client.post(
        "/products/",
        json={
            "name": "",
            "description": "Invalid product",
            "brand": "Test Brand",
            "category_id": category["id"],
        },
        headers=admin_headers,
    )

    assert response.status_code in [400, 422], response.text
