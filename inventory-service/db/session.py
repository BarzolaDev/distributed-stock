from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

load_dotenv()

def get_engine():
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@inventory-db:5432/inventory")
    return create_engine(DATABASE_URL)

def get_db():
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()