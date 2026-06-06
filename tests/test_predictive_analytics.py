def assert_ml_response(response):
    assert response.status_code == 200, response.text

    data = response.json()

    assert "title" in data
    assert "summary" in data
    assert "data" in data

    assert isinstance(data["title"], str)
    assert isinstance(data["summary"], str)
    assert data["title"] != ""
    assert data["summary"] != ""

    return data


def test_analytics_summary(client, admin_headers):
    response = client.get("/ml/summary", headers=admin_headers)
    data = assert_ml_response(response)

    assert data["title"] == "Analytics Overview"
    assert "metrics" in data["data"]
    assert "modules" in data["data"]


def test_sales_forecast(client, admin_headers):
    response = client.get(
        "/ml/sales-forecast?days=7&lookback_days=30",
        headers=admin_headers,
    )

    data = assert_ml_response(response)

    assert data["title"] == "Sales Forecast"
    assert "metrics" in data["data"]
    assert "rows" in data["data"]
    assert isinstance(data["data"]["rows"], list)


def test_stock_risk_prediction(client, admin_headers):
    response = client.get(
        "/ml/low-stock-prediction?lookback_days=30",
        headers=admin_headers,
    )

    data = assert_ml_response(response)

    assert data["title"] == "Stock Risk Prediction"
    assert "metrics" in data["data"]
    assert "rows" in data["data"]
    assert isinstance(data["data"]["rows"], list)


def test_restock_plan(client, admin_headers):
    response = client.get(
        "/ml/reorder-recommendations?lookback_days=30&lead_time_days=7&safety_days=5",
        headers=admin_headers,
    )

    data = assert_ml_response(response)

    assert data["title"] == "Restock Plan"
    assert "metrics" in data["data"]
    assert "rows" in data["data"]
    assert isinstance(data["data"]["rows"], list)


def test_customer_insights(client, admin_headers):
    response = client.get("/ml/customer-segments", headers=admin_headers)
    data = assert_ml_response(response)

    assert data["title"] == "Customer Insights"
    assert "metrics" in data["data"]
    assert "rows" in data["data"]
    assert isinstance(data["data"]["rows"], list)


def test_product_recommendations(client, admin_headers):
    response = client.get(
        "/ml/product-recommendations?limit=10",
        headers=admin_headers,
    )

    data = assert_ml_response(response)

    assert data["title"] == "Product Recommendations"
    assert "metrics" in data["data"]
    assert "rows" in data["data"]
    assert isinstance(data["data"]["rows"], list)


def test_customer_based_product_recommendations(client, admin_headers):
    response = client.get(
        "/ml/product-recommendations/1?limit=10",
        headers=admin_headers,
    )

    data = assert_ml_response(response)

    assert data["title"] == "Product Recommendations"
    assert "metrics" in data["data"]
    assert "rows" in data["data"]
    assert isinstance(data["data"]["rows"], list)
