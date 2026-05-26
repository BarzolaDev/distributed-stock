import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .account import Base

class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False, default="completed")
    response = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
