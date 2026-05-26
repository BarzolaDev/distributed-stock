from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from db.session import get_db
from services.order import create_order
from domain.exceptions import PaymentFailedError, InventoryFailedError

router = APIRouter()

@router.post("/orders")
def place_order(account_id: UUID, product_id: UUID, quantity: int, amount: int, idempotency_key: str, db: Session = Depends(get_db)):
    try:
        return create_order(account_id, product_id, quantity, amount, idempotency_key, db)
    except PaymentFailedError:
        raise HTTPException(status_code=400, detail="Payment failed")
    except InventoryFailedError:
        raise HTTPException(status_code=400, detail="Insufficient stock, payment refunded")
