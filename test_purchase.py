import httpx

INVENTORY_URL = "http://localhost:8001"
PAYMENT_URL = "http://localhost:8002"

def purchase(product_id: int, account_id: int, quantity: int, amount: int):
    # Paso 1 — cobrar
    payment = httpx.post(f"{PAYMENT_URL}/accounts/{account_id}/charge", params={"amount": amount})
    
    if payment.status_code != 200:
        print(f"❌ Pago falló: {payment.json()}")
        return
    
    print(f"✅ Pago procesado: {payment.json()}")
    
    # Simulamos falla del inventory service
    raise Exception("💥 Inventory service cayó")
    
    # Este código nunca se ejecuta
    stock = httpx.post(f"{INVENTORY_URL}/products/{product_id}/reserve", params={"quantity": quantity})
    print(f"✅ Stock descontado: {stock.json()}")

if __name__ == "__main__":
    try:
        purchase(product_id=1, account_id=1, quantity=1, amount=100)
    except Exception as e:
        print(f"{e}")
        print("💀 INCONSISTENCIA — el pago se procesó pero el stock NO se descontó")