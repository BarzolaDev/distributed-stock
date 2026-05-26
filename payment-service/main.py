from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from db.session import get_db
from models.account import Account
from routes.payment import router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    from db.session import get_engine
    from models.account import Base
    from models.idempotency import IdempotencyKey
    Base.metadata.create_all(bind=get_engine())
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router)

@app.get("/health")
def health():
    return {"service": "payment", "status": "ok"}

@app.post("/seed")
def seed(db: Session = Depends(get_db)):
    account = Account(owner="Test User", balance=1000)
    db.add(account)
    db.commit()
    db.refresh(account)
    return {"account_id": str(account.id), "balance": account.balance}

@app.get("/accounts/{account_id}/balance")
def get_balance(account_id: UUID, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": str(account.id), "balance": account.balance}
