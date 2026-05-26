from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from models.product import Product
from routes.product import router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    from db.session import get_engine
    from models.product import Base
    Base.metadata.create_all(bind=get_engine())
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router)

@app.get("/health")
def health():
    return {"service": "inventory", "status": "ok"}

@app.post("/seed")
def seed(db: Session = Depends(get_db)):
    product = Product(name="Test Product", stock=10)
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"product_id": product.id, "stock": product.stock}

@app.get("/products/{product_id}/stock")
def get_stock(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product_id": product.id, "stock": product.stock}
