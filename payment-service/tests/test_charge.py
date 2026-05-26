import uuid
from models.account import Account

def test_charge_success(client, db_session):
    account = Account(owner="Test User", balance=1000)
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)

    response = client.post(f"/accounts/{account.id}/charge?amount=100&idempotency_key=key-1")
    
    assert response.status_code == 200
    assert response.json()["remaining_balance"] == 900

def test_charge_insufficient_balance(client, db_session):
    account = Account(owner="Test User", balance=50)
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)

    response = client.post(f"/accounts/{account.id}/charge?amount=100&idempotency_key=key-2")
    
    assert response.status_code == 400

def test_charge_account_not_found(client):
    fake_id = uuid.uuid4()
    response = client.post(f"/accounts/{fake_id}/charge?amount=100&idempotency_key=key-3")
    
    assert response.status_code == 404

def test_idempotency(client, db_session):
    account = Account(owner="Test User", balance=1000)
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)

    client.post(f"/accounts/{account.id}/charge?amount=100&idempotency_key=key-4")
    response = client.post(f"/accounts/{account.id}/charge?amount=100&idempotency_key=key-4")
    
    assert response.status_code == 200
    db_session.refresh(account)
    assert account.balance == 900
