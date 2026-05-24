## The Race Condition Problem

SELECT FOR UPDATE was missing inside each service.
20 concurrent requests hitting the same balance = wrong numbers.

Without lock: balance never reached 0, requests overwrote each other.

## The Fix

Added SELECT FOR UPDATE to payment and inventory services.

```python
account = db.query(Account).filter(Account.id == account_id).with_for_update().first()
```

## Proof — Tested with RaceHunter

20 concurrent requests, balance 1000, charge 100:

✅ 200 → 10 times (processed)
❌ 400 → 10 times (insufficient balance)
💰 Final balance: 0 (exact, never negative)

Same result for inventory service. Lock works.