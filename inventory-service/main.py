from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db, engine
from models.product import Base, Product

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health")
def health():
    return {"service": "inventory", "status": "ok"}

@app.post("/products/{product_id}/reserve")
def reserve_stock(product_id: int, quantity: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    product.stock -= quantity
    db.commit()
    
    return {"product_id": product_id, "remaining_stock": product.stock}

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