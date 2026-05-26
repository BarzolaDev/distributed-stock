import httpx
from sqlalchemy.orm import Session
from uuid import UUID
from models.order import Order
from domain.exceptions import PaymentFailedError, InventoryFailedError
from services.circuit_breaker import inventory_circuit, payment_circuit
import os

PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8000")
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://inventory-service:8000")

def create_order(account_id: UUID, product_id: UUID, quantity: int, amount: int, idempotency_key: str, db: Session) -> dict:
    existing = db.query(Order).filter(Order.idempotency_key == idempotency_key).first()
    if existing:
        return {"order_id": str(existing.id), "account_id": str(existing.account_id), "product_id": str(existing.product_id), "quantity": existing.quantity, "amount": existing.amount, "status": existing.status}

    try:
        payment_response = payment_circuit.call(
            httpx.post,
            f"{PAYMENT_SERVICE_URL}/accounts/{account_id}/charge",
            params={"amount": amount, "idempotency_key": idempotency_key}
        )
    except Exception:
        raise PaymentFailedError("Payment service unavailable")

    if payment_response.status_code != 200:
        raise PaymentFailedError("Payment failed")

    try:
        inventory_response = inventory_circuit.call(
            httpx.post,
            f"{INVENTORY_SERVICE_URL}/products/{product_id}/reserve",
            params={"quantity": quantity, "idempotency_key": idempotency_key}
        )
    except Exception:
        httpx.post(
            f"{PAYMENT_SERVICE_URL}/accounts/{account_id}/refund",
            params={"amount": amount}
        )
        raise InventoryFailedError("Inventory service unavailable, payment refunded")

    if inventory_response.status_code != 200:
        httpx.post(
            f"{PAYMENT_SERVICE_URL}/accounts/{account_id}/refund",
            params={"amount": amount}
        )
        raise InventoryFailedError("Inventory reservation failed, payment refunded")

    order = Order(
        account_id=account_id,
        product_id=product_id,
        quantity=quantity,
        amount=amount,
        status="confirmed",
        idempotency_key=idempotency_key
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return {"order_id": str(order.id), "account_id": str(account_id), "product_id": str(product_id), "quantity": quantity, "amount": amount, "status": "confirmed"}
