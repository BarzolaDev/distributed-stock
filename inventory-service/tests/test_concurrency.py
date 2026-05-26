import threading
import requests
import uvicorn
import time
import uuid
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.product import Product, Base
from main import app
from db.session import get_db

def test_no_negative_stock(postgres, db_engine):
    os.environ["DATABASE_URL"] = postgres.get_connection_url()

    SessionLocal = sessionmaker(bind=db_engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    db = SessionLocal()
    product = Product(name="Test Product", stock=10)
    db.add(product)
    db.commit()
    db.refresh(product)
    product_id = product.id
    db.close()

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8001, log_level="error"))
    t = threading.Thread(target=server.run)
    t.daemon = True
    t.start()
    time.sleep(2)

    results = []

    def reserve():
        key = str(uuid.uuid4())
        try:
            response = requests.post(f"http://127.0.0.1:8001/products/{product_id}/reserve?quantity=1&idempotency_key={key}")
            results.append(response.status_code)
        except Exception as e:
            results.append(0)

    threads = [threading.Thread(target=reserve) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    server.should_exit = True
    app.dependency_overrides.clear()

    print(f"\n200: {results.count(200)}, 400: {results.count(400)}, errors: {results.count(0)}")

    assert results.count(200) == 10
    assert results.count(400) == 10
