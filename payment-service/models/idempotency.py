from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .account import Base

class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    
    id = Column(Integer, primary_key=True)
    key = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False, default="completed")
    response = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())