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
    
    try:
        # Paso 2 — descontar stock
        stock = httpx.post(f"{INVENTORY_URL}/products/{product_id}/reserve", params={"quantity": quantity})
        
        if stock.status_code != 200:
            raise Exception(f"Stock falló: {stock.json()}")
        
        print(f"✅ Stock descontado: {stock.json()}")
        print("🎉 Compra completada — sistema consistente")
        
    except Exception as e:
        print(f"❌ {e}")
        print("↩️ Inventory caído — revertiendo pago...")
        refund = httpx.post(f"{PAYMENT_URL}/accounts/{account_id}/refund", params={"amount": amount})
        print(f"✅ Pago revertido: {refund.json()}")
        print("✅ Sistema consistente — Saga ejecutada")

if __name__ == "__main__":
    purchase(product_id=1, account_id=1, quantity=1, amount=100)