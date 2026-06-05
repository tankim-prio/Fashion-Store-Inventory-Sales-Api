def create_category_product(client, headers):
    category_response = client.post(
        "/categories/",
        json={
            "name": "Shirt",
            "description": "Men shirt"
        },
        headers=headers
    )

    category_id = category_response.json()["id"]

    product_response = client.post(
        "/products/",
        json={
            "name": "Formal Shirt",
            "category_id": category_id,
            "brand": "Anchor",
            "description": "Formal shirt"
        },
        headers=headers
    )

    return product_response.json()["id"]


def test_create_variant(client, admin_headers):
    product_id = create_category_product(client, admin_headers)

    response = client.post(
        "/variants/",
        json={
            "product_id": product_id,
            "size": "L",
            "color": "White",
            "buy_price": 500,
            "sell_price": 900,
            "stock_quantity": 20,
            "sku": "SHIRT-WHITE-L-TEST"
        },
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == product_id
    assert data["sku"] == "SHIRT-WHITE-L-TEST"
    assert data["stock_quantity"] == 20


def test_variant_sell_price_lower_than_buy_price_blocked(client, admin_headers):
    product_id = create_category_product(client, admin_headers)

    response = client.post(
        "/variants/",
        json={
            "product_id": product_id,
            "size": "L",
            "color": "Black",
            "buy_price": 500,
            "sell_price": 400,
            "stock_quantity": 10,
            "sku": "BAD-SKU-TEST"
        },
        headers=admin_headers
    )

    assert response.status_code == 422
    assert response.json()["success"] is False


def test_add_stock(client, admin_headers):
    product_id = create_category_product(client, admin_headers)

    variant_response = client.post(
        "/variants/",
        json={
            "product_id": product_id,
            "size": "M",
            "color": "Blue",
            "buy_price": 400,
            "sell_price": 700,
            "stock_quantity": 5,
            "sku": "SHIRT-BLUE-M-TEST"
        },
        headers=admin_headers
    )

    variant_id = variant_response.json()["id"]

    response = client.post(
        "/stock/add",
        json={
            "variant_id": variant_id,
            "quantity": 10,
            "note": "Test stock add",
            "created_by": "admin@test.com"
        },
        headers=admin_headers
    )

    assert response.status_code == 200


def test_add_stock_zero_quantity_blocked(client, admin_headers):
    response = client.post(
        "/stock/add",
        json={
            "variant_id": 1,
            "quantity": 0,
            "note": "Bad stock",
            "created_by": "admin@test.com"
        },
        headers=admin_headers
    )

    assert response.status_code == 422
    assert response.json()["success"] is False
