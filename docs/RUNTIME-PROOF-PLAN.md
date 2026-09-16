# AGRI-CI v0.24 Runtime Proof

The release-candidate decision must be based on execution, not source-code presence.

CI proof order:
1. start PostgreSQL 16 + Redis;
2. install backend dependencies;
3. run `alembic upgrade head`;
4. import FastAPI application;
5. verify commercial route inventory;
6. run AGRI-CI-001 deterministic state-machine invariants;
7. run PostgreSQL relational seed;
8. run two-session Koffi 400 kg race;
9. run persisted idempotency replay + changed-payload rejection;
10. run HTTP security harness.

A green result still does not certify an external payment provider, production TLS,
backup restore, monitoring, legal/privacy documents, or real field operations.
