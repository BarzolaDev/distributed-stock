import requests
import uuid

BASE = "http://localhost:8003"
PAYMENT = "http://localhost:8002"
INVENTORY = "http://localhost:8001"

def test_full_order_flow():
    product = requests.post(f"{INVENTORY}/seed").json()
    account = requests.post(f"{PAYMENT}/seed").json()
    
    product_id = product["product_id"]
    account_id = account["account_id"]
    key = str(uuid.uuid4())

    response = requests.post(f"{BASE}/orders", params={
        "account_id": account_id,
        "product_id": product_id,
        "quantity": 2,
        "amount": 200,
        "idempotency_key": key
    })

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"

    balance = requests.get(f"{PAYMENT}/accounts/{account_id}/balance").json()
    stock = requests.get(f"{INVENTORY}/products/{product_id}/stock").json()

    assert balance["balance"] == 800
    assert stock["stock"] == 8

def test_saga_compensation():
    account = requests.post(f"{PAYMENT}/seed").json()
    account_id = account["account_id"]
    fake_product_id = str(uuid.uuid4())
    key = str(uuid.uuid4())

    response = requests.post(f"{BASE}/orders", params={
        "account_id": account_id,
        "product_id": fake_product_id,
        "quantity": 2,
        "amount": 200,
        "idempotency_key": key
    })

    assert response.status_code == 400

    balance = requests.get(f"{PAYMENT}/accounts/{account_id}/balance").json()
    assert balance["balance"] == 1000

def test_idempotency():
    product = requests.post(f"{INVENTORY}/seed").json()
    account = requests.post(f"{PAYMENT}/seed").json()
    
    product_id = product["product_id"]
    account_id = account["account_id"]
    key = str(uuid.uuid4())

    requests.post(f"{BASE}/orders", params={
        "account_id": account_id,
        "product_id": product_id,
        "quantity": 2,
        "amount": 200,
        "idempotency_key": key
    })

    requests.post(f"{BASE}/orders", params={
        "account_id": account_id,
        "product_id": product_id,
        "quantity": 2,
        "amount": 200,
        "idempotency_key": key
    })

    balance = requests.get(f"{PAYMENT}/accounts/{account_id}/balance").json()
    assert balance["balance"] == 800
