# distributed-stock

A distributed payment system built to handle race conditions, duplicate requests, and distributed consistency.

Not a tutorial project. Built by breaking things intentionally and fixing them with proof.

---

## The Problem

Most systems fail under concurrency, not under normal load.
Request 1 reads stock → 1
Request 2 reads stock → 1  ← before Request 1 writes
Request 1 writes      → 0
Request 2 writes      → 0  ← should have failed

This repo demonstrates the failure, implements the fix, and proves it works under load.

---

## Architecture
client → order-service → payment-service
→ inventory-service

Three independent services. One consistent outcome.

Each service has its own database. No shared state.

---

## Solutions

### SELECT FOR UPDATE
Pessimistic lock at the database level.
Concurrent requests cannot read stale values before mutation.

Chosen over optimistic locking because concurrent payments need guaranteed consistency, not retries.

```python
account = db.query(Account).filter(Account.id == account_id).with_for_update().first()
```

### Idempotency
Same request sent N times = processed only once.
Each service stores the `idempotency_key` and returns the cached response on duplicates.

SELECT FOR UPDATE and idempotency solve different problems:
- SELECT FOR UPDATE → different requests hitting the same resource
- Idempotency → same request arriving multiple times

Both are necessary.

### Saga
Payment and inventory must succeed together or not at all.

If inventory fails after payment → automatic refund.
If payment fails → inventory never touched.

Chosen over 2PC because Two-Phase Commit blocks all services while waiting for confirmation.
Under high concurrency that kills throughput. Saga compensates on failure without blocking.

---

## Proof

Tested with RaceHunter — a concurrent load testing tool built in Go for this project.

20 concurrent requests, balance 1000, charge 100:
✅ 200 → 10 times (processed)
❌ 400 → 10 times (insufficient balance)
💰 Final balance: 0 — exact, never negative

Same result for inventory service.

---

## Testing

### Unit & Contract
Each service has contract tests — full HTTP flow per endpoint.

### Concurrency
Real PostgreSQL via Testcontainers, not mocks.
SQLite does not support SELECT FOR UPDATE.
Concurrency tests run against real PostgreSQL to validate locking behavior.

### Integration
End-to-end flow across all 3 services.
docker-compose spun up and torn down automatically by the test suite.

---

## Stack

Python · FastAPI · PostgreSQL · SQLAlchemy · Docker  
Go · RaceHunter  
Testcontainers · Pytest · GitHub Actions

---

## Known Limitations

- HTTPS not configured — requires a domain and certificate (Let's Encrypt)
- CORS set to * — should be restricted to specific domains in production
- No distributed tracing — requests cannot be traced across services

