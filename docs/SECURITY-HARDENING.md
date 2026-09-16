# AGRI-CI Security Hardening Status

## Implemented foundations
- JWT access + refresh flow
- password hashing
- standardized HTTP error handler
- reusable RBAC dependency
- row locking for quantity-sensitive flows
- audit log
- transactional domain-event/outbox table and worker seam
- persisted idempotency table
- persisted idempotency helper
- idempotency uniqueness at database level
- idempotency wired to aggregation creation and order creation
- payment preparation restricted to OPERATIONS_MANAGER / ADMIN
- object ownership checks on buyer demand/order flows

## Still mandatory before production
- wire idempotency to every sensitive mutation (commitments, collection, lots, transport, delivery, provider callbacks)
- complete endpoint-by-endpoint RBAC matrix
- signed payment-provider webhook; remove development provider-success seam
- refresh token revocation/rotation policy
- production CORS, rate limiting and secrets management
- run Alembic against real PostgreSQL
- execute real concurrent reservation test
- execute full HTTP AGRI-CI-001 E2E test
- CI workflow with PostgreSQL service
- broker/notification adapter for outbox worker
- backup/restore drill and production observability
