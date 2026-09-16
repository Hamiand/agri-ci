# AGRI-CI HTTP E2E Status

## Now executable in PostgreSQL CI
- Alembic migration chain
- FastAPI application import
- `/health`
- anonymous-access rejection for protected farmer endpoint
- PostgreSQL two-session 400 kg concurrency race
- AGRI-CI-001 relational supply seed
- machine-readable AGRI-CI-001 invariants

## Deliberately not overstated
The current HTTP test is an authenticated/security harness, not yet the complete 16-step
business transaction through public endpoints. The repository's schemas evolved during
v0.1–v0.19, so the next increment should use the CI route inventory and runtime failures to
stabilize factories before claiming full HTTP E2E.

## Full HTTP target
register/login → farmer/farm/plot/harvest/offer → buyer/demand → matching → aggregation →
commitment decline/accept → replacement → order → collection → quality → lot → transport →
delivery → settlement → farmer money.
