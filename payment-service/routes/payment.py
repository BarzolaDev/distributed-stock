from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from services.payment import charge, refund
from domain.exceptions import AccountNotFoundError, InsufficientBalanceError

router = APIRouter()

@router.post("/accounts/{account_id}/charge")
def charge_account(account_id: int, amount: int, idempotency_key: str, db: Session = Depends(get_db)):
    try:
        return charge(account_id, amount, idempotency_key, db)
    except AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")
    except InsufficientBalanceError:
        raise HTTPException(status_code=400, detail="Insufficient balance")

@router.post("/accounts/{account_id}/refund")
def refund_account(account_id: int, amount: int, db: Session = Depends(get_db)):
    try:
        return refund(account_id, amount, db)
    except AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")
