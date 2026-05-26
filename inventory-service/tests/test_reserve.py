import uuid
from models.product import Product

def test_reserve_success(client, db_session):
    product = Product(name="Test Product", stock=10)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    response = client.post(f"/products/{product.id}/reserve?quantity=3&idempotency_key=key-1")
    
    assert response.status_code == 200
    assert response.json()["remaining_stock"] == 7

def test_reserve_insufficient_stock(client, db_session):
    product = Product(name="Test Product", stock=2)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    response = client.post(f"/products/{product.id}/reserve?quantity=5&idempotency_key=key-2")
    
    assert response.status_code == 400

def test_reserve_product_not_found(client):
    fake_id = uuid.uuid4()
    response = client.post(f"/products/{fake_id}/reserve?quantity=1&idempotency_key=key-3")
    
    assert response.status_code == 404
