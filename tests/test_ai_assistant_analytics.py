def assert_ai_response(response):
    assert response.status_code == 200, response.text

    data = response.json()

    assert "answer" in data
    assert "data" in data
    assert "suggestions" in data

    assert isinstance(data["answer"], str)
    assert data["answer"] != ""

    return data


def test_ai_analytics_overview(client, admin_headers):
    response = client.post(
        "/ai/chat",
        json={"question": "show analytics overview"},
        headers=admin_headers,
    )

    data = assert_ai_response(response)

    assert "analytics" in data["answer"].lower() or data["data"] is not None


def test_ai_sales_forecast(client, admin_headers):
    response = client.post(
        "/ai/chat",
        json={"question": "forecast next 7 days sales"},
        headers=admin_headers,
    )

    data = assert_ai_response(response)

    assert "sales" in data["answer"].lower() or data["data"] is not None


def test_ai_restock_plan(client, admin_headers):
    response = client.post(
        "/ai/chat",
        json={"question": "which products should I restock?"},
        headers=admin_headers,
    )

    data = assert_ai_response(response)

    assert "restock" in data["answer"].lower() or data["data"] is not None


def test_ai_customer_insights(client, admin_headers):
    response = client.post(
        "/ai/chat",
        json={"question": "show customer insights"},
        headers=admin_headers,
    )

    data = assert_ai_response(response)

    assert "customer" in data["answer"].lower() or data["data"] is not None


def test_ai_product_recommendations(client, admin_headers):
    response = client.post(
        "/ai/chat",
        json={"question": "recommend products for customer 1"},
        headers=admin_headers,
    )

    data = assert_ai_response(response)

    assert "product" in data["answer"].lower() or data["data"] is not None


def test_ai_paid_customers_still_works(client, admin_headers):
    response = client.post(
        "/ai/chat",
        json={"question": "who bought products and paid?"},
        headers=admin_headers,
    )

    data = assert_ai_response(response)

    assert "paid" in data["answer"].lower() or data["data"] is not None
