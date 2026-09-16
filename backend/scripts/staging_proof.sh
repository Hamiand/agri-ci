#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
: "${POSTGRES_PASSWORD:=agrci-staging-change-me}"
export POSTGRES_PASSWORD
docker compose -f docker-compose.staging.yml up -d postgres redis
trap 'docker compose -f docker-compose.staging.yml down' EXIT
cd backend
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://agrci:${POSTGRES_PASSWORD}@localhost:5432/agrci}"
export TEST_DATABASE_URL="$DATABASE_URL"
export JWT_SECRET="${JWT_SECRET:-staging-proof-secret-change-me-please}"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e . --no-build-isolation
python scripts/dependency_doctor.py
alembic upgrade head
python -c "from app.main import app; print(app.title, len(app.routes))"
pytest -q
