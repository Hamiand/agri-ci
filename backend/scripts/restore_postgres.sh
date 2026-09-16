#!/usr/bin/env bash
set -euo pipefail
: "${DATABASE_URL:?DATABASE_URL required}"
: "${1:?usage: restore_postgres.sh backup.dump}"
pg_restore --clean --if-exists --no-owner --no-acl --dbname="$DATABASE_URL" "$1"
