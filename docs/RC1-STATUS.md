# AGRI-CI RC1 Status — v0.28

The source repository now contains the principal deployment controls for a controlled pilot:
environment-driven CORS, security headers, request IDs, signed payment webhook seam,
preflight secret checks, container healthcheck, PostgreSQL backup/restore scripts,
commercial gate documents, concurrency/idempotency test suites and CI services.

**RC1 is still not declared.**

The remaining software proof is execution, not another feature:
1. PostgreSQL/Alembic CI green;
2. PostgreSQL concurrency test green;
3. persisted idempotency replay test green;
4. complete authenticated AGRI-CI-001 public HTTP flow green.

After those pass, external launch gates remain: licensed payment provider certification,
TLS/DNS/hosting, backup restore drill, monitoring, legal/privacy review and real pilot partners.
