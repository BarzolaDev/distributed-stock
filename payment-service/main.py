from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db, engine
from models.account import Base, Account

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health")
def health():
    return {"service": "payment", "status": "ok"}

@app.post("/accounts/{account_id}/charge")
def charge(account_id: int, amount: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    account.balance -= amount
    db.commit()
    
    return {"account_id": account_id, "remaining_balance": account.balance}

@app.post("/seed")
def seed(db: Session = Depends(get_db)):
    account = Account(owner="Test User", balance=1000)
    db.add(account)
    db.commit()
    db.refresh(account)
    return {"account_id": account.id, "balance": account.balance}

@app.get("/accounts/{account_id}/balance")
def get_balance(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": account.id, "balance": account.balance}