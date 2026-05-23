# distributed-stock

## The Problem

SELECT FOR UPDATE solves concurrency within a single database.
But what happens when a purchase requires two services — payment and inventory — each with their own database?

Payment processed. Inventory service down. Stock never updated.
The customer paid. The stock didn't move. The system is inconsistent.

## The Evidence

Payment processed, inventory crashed:
✅ Pago procesado: {'account_id': 1, 'remaining_balance': 400}
❌ [Errno 111] Connection refused
💀 INCONSISTENCIA — pago procesado pero stock NO descontado

## The Defense — Saga Pattern

If inventory fails after payment is processed, a compensating transaction reverts the payment automatically.

Both or nothing.

✅ Pago procesado: {'account_id': 1, 'remaining_balance': 400}
❌ [Errno 111] Connection refused
↩️ Inventory caído — revertiendo pago...
✅ Pago revertido: {'account_id': 1, 'remaining_balance': 500}
✅ Sistema consistente — Saga ejecutada

## Stack
FastAPI · PostgreSQL · Docker Compose · Python