from sqlalchemy.orm import Session
from uuid import UUID
from models.product import Product
from models.idempotency import IdempotencyKey
from domain.exceptions import ProductNotFoundError, InsufficientStockError

def reserve_stock(product_id: UUID, quantity: int, idempotency_key: str, db: Session) -> dict:
    existing = db.query(IdempotencyKey).filter(IdempotencyKey.key == idempotency_key).first()
    if existing:
        return {"product_id": str(product_id), "remaining_stock": int(existing.response)}

    product = db.query(Product).filter(Product.id == product_id).with_for_update().first()
    
    if not product:
        raise ProductNotFoundError(f"Product {product_id} not found")
    
    if product.stock < quantity:
        raise InsufficientStockError(f"Insufficient stock for product {product_id}")
    
    product.stock -= quantity
    db.commit()

    record = IdempotencyKey(key=idempotency_key, response=str(product.stock))
    db.add(record)
    db.commit()

    return {"product_id": str(product_id), "remaining_stock": product.stock}
