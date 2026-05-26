from sqlalchemy.orm import Session
from models.account import Account
from models.idempotency import IdempotencyKey
from domain.exceptions import AccountNotFoundError, InsufficientBalanceError

def charge(account_id: int, amount: int, idempotency_key: str, db: Session) -> dict:
    existing = db.query(IdempotencyKey).filter(
        IdempotencyKey.key == idempotency_key
    ).first()
    
    if existing:
        return existing.response

    account = db.query(Account).filter(Account.id == account_id).with_for_update().first()
    
    if not account:
        raise AccountNotFoundError(f"Account {account_id} not found")
    
    if account.balance < amount:
        raise InsufficientBalanceError(f"Insufficient balance for account {account_id}")
    
    account.balance -= amount
    
    response = {"account_id": account_id, "remaining_balance": account.balance}
    record = IdempotencyKey(key=idempotency_key, response=str(response))
    db.add(record)
    db.commit()
    
    return response

def refund(account_id: int, amount: int, db: Session) -> dict:
    account = db.query(Account).filter(Account.id == account_id).first()
    
    if not account:
        raise AccountNotFoundError(f"Account {account_id} not found")
    
    account.balance += amount
    db.commit()
    
    return {"account_id": account_id, "remaining_balance": account.balance}
