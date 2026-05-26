from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from services.inventory import reserve_stock
from domain.exceptions import ProductNotFoundError, InsufficientStockError

router = APIRouter()

@router.post("/products/{product_id}/reserve")
def reserve(product_id: int, quantity: int, idempotency_key: str, db: Session = Depends(get_db)):
    try:
        return reserve_stock(product_id, quantity, idempotency_key, db)
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")
    except InsufficientStockError:
        raise HTTPException(status_code=400, detail="Insufficient stock")
