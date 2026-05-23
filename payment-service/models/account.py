from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    owner = Column(String, nullable=False)
    balance = Column(Integer, nullable=False, default=0)