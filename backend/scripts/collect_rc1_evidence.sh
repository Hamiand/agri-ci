#!/usr/bin/env bash
set -euo pipefail
rm -rf .rc1-evidence
mkdir -p .rc1-evidence
alembic upgrade head
touch .rc1-evidence/postgres_migrations.green
pytest -q tests/integration/test_offer_locking_postgres.py
touch .rc1-evidence/concurrency.green
pytest -q tests/integration/test_idempotency_postgres.py
touch .rc1-evidence/idempotency.green
pytest -q tests/integration/test_authenticated_http_security.py tests/integration/test_agrici001_http_e2e.py
touch .rc1-evidence/http_e2e.green
python scripts/write_evidence_metadata.py
python scripts/create_rc1_certificate.py
echo "Runtime evidence collected."
