import pytest
import uuid
from unittest.mock import patch, MagicMock

ACCOUNT_ID = uuid.uuid4()
PRODUCT_ID = uuid.uuid4()

def mock_payment_success(url, **kwargs):
    response = MagicMock()
    response.status_code = 200
    return response

def mock_inventory_success(url, **kwargs):
    response = MagicMock()
    response.status_code = 200
    return response

def mock_inventory_failure(url, **kwargs):
    response = MagicMock()
    response.status_code = 400
    return response

def test_create_order_success(client):
    with patch("httpx.post", side_effect=[mock_payment_success(""), mock_inventory_success("")]):
        response = client.post(f"/orders?account_id={ACCOUNT_ID}&product_id={PRODUCT_ID}&quantity=2&amount=200&idempotency_key=order-1")
        assert response.status_code == 200
        assert response.json()["status"] == "confirmed"

def test_create_order_payment_fails(client):
    with patch("httpx.post", return_value=mock_inventory_failure("")):
        response = client.post(f"/orders?account_id={ACCOUNT_ID}&product_id={PRODUCT_ID}&quantity=2&amount=200&idempotency_key=order-2")
        assert response.status_code == 400

def test_create_order_inventory_fails_refund_triggered(client):
    refund_called = []

    def mock_calls(url, **kwargs):
        response = MagicMock()
        if "charge" in url:
            response.status_code = 200
        elif "reserve" in url:
            response.status_code = 400
        elif "refund" in url:
            refund_called.append(True)
            response.status_code = 200
        return response

    with patch("httpx.post", side_effect=mock_calls):
        response = client.post(f"/orders?account_id={ACCOUNT_ID}&product_id={PRODUCT_ID}&quantity=2&amount=200&idempotency_key=order-3")
        assert response.status_code == 400
        assert len(refund_called) == 1

def test_idempotency(client):
    with patch("httpx.post", side_effect=[mock_payment_success(""), mock_inventory_success("")]):
        client.post(f"/orders?account_id={ACCOUNT_ID}&product_id={PRODUCT_ID}&quantity=2&amount=200&idempotency_key=order-4")
    
    with patch("httpx.post") as mock:
        response = client.post(f"/orders?account_id={ACCOUNT_ID}&product_id={PRODUCT_ID}&quantity=2&amount=200&idempotency_key=order-4")
        assert response.status_code == 200
        mock.assert_not_called()
