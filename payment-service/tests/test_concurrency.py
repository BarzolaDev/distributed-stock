import threading
import requests
import uvicorn
import time
import uuid
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.account import Account, Base
from main import app
from db.session import get_db

def test_no_negative_balance(postgres, db_engine):
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
    account = Account(owner="Test User", balance=1000)
    db.add(account)
    db.commit()
    db.refresh(account)
    account_id = account.id
    db.close()

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8011, log_level="error"))
    t = threading.Thread(target=server.run)
    t.daemon = True
    t.start()
    time.sleep(2)

    results = []

    def charge():
        key = str(uuid.uuid4())
        try:
            response = requests.post(
                f"http://127.0.0.1:8011/accounts/{account_id}/charge",
                params={"amount": 100, "idempotency_key": key}
            )
            results.append(response.status_code)
        except Exception as e:
            print(f"Error: {e}")
            results.append(0)

    threads = [threading.Thread(target=charge) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    server.should_exit = True
    app.dependency_overrides.clear()

    print(f"\n200: {results.count(200)}, 400: {results.count(400)}, errors: {results.count(0)}")

    assert results.count(200) == 10
    assert results.count(400) == 10
