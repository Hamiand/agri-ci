#!/usr/bin/env sh
set -eu
python -m compileall -q app tests
pytest -q
alembic upgrade head
pytest -q tests/integration
