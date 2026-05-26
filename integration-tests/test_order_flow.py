import requests
import uuid

BASE = "http://localhost:8003"
PAYMENT = "http://localhost:8002"
INVENTORY = "http://localhost:8001"

def test_full_order_flow():
    # Seed
    product = requests.post(f"{INVENTORY}/seed").json()
    account = requests.post(f"{PAYMENT}/seed").json()
    
    product_id = product["product_id"]
    account_id = account["account_id"]
    key = str(uuid.uuid4())

    # Crear orden
    response = requests.post(f"{BASE}/orders", params={
        "account_id": account_id,
        "product_id": product_id,
        "quantity": 2,
        "amount": 200,
        "idempotency_key": key
    })

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"

    # Verificar balance y stock
    balance = requests.get(f"{PAYMENT}/accounts/{account_id}/balance").json()
    stock = requests.get(f"{INVENTORY}/products/{product_id}/stock").json()

    assert balance["balance"] == 800
    assert stock["stock"] == 8

def test_saga_compensation():
    account = requests.post(f"{PAYMENT}/seed").json()
    account_id = account["account_id"]
    key = str(uuid.uuid4())

    # Producto inexistente — inventory falla → refund automático
    response = requests.post(f"{BASE}/orders", params={
        "account_id": account_id,
        "product_id": 99999,
        "quantity": 2,
        "amount": 200,
        "idempotency_key": key
    })

    assert response.status_code == 400

    # Balance debe estar intacto
    balance = requests.get(f"{PAYMENT}/accounts/{account_id}/balance").json()
    assert balance["balance"] == 1000

def test_idempotency():
    product = requests.post(f"{INVENTORY}/seed").json()
    account = requests.post(f"{PAYMENT}/seed").json()
    
    product_id = product["product_id"]
    account_id = account["account_id"]
    key = str(uuid.uuid4())

    # Misma orden dos veces
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

    # Balance descontado solo una vez
    balance = requests.get(f"{PAYMENT}/accounts/{account_id}/balance").json()
    assert balance["balance"] == 800
