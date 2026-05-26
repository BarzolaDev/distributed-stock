from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="confirmed")
    idempotency_key = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())
