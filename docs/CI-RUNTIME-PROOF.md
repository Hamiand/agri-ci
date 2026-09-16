# AGRI-CI v0.31 — CI Runtime Proof

The GitHub Actions workflow now contains an executable `rc1-runtime-proof` job.

It starts PostgreSQL 16 and Redis 7, installs the backend, runs preflight, applies Alembic,
executes the concurrency/idempotency/HTTP proof tests, enforces the RC1 gate, and uploads
the evidence directory.

Evidence is deleted at the start of every run, so stale `.green` files cannot make a failed
run appear successful. The evidence directory is gitignored.

If all four runtime proofs pass, CI creates `RC1-CERTIFICATE.json`. This certificate covers
the software runtime gate only. It does not certify the payment provider, production hosting,
legal/privacy compliance, backup restore, monitoring or real field operations.

## What must happen next
Push this repository to the GitHub repository that will host AGRI-CI and run the workflow.
The resulting CI log is now the authoritative source for the next code corrections.
