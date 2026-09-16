# AGRI-CI RC1 Audit Summary — v0.26

## Actually passed locally
- Python compilation: YES
- structural commercial gate: YES
- backup/restore shell syntax: YES
- Python dependency installation: NO
- non-PostgreSQL unit suite: NOT RUN / FAILED
- FastAPI import smoke: NOT RUN / FAILED

## Cannot be proved locally here
Docker: not available
PostgreSQL client/server: not available

Therefore the PostgreSQL migration, concurrency, idempotency replay and full database E2E
remain release blockers until executed in CI/staging.

## One-command staging proof
On a machine with Docker:
`bash backend/scripts/staging_proof.sh`
