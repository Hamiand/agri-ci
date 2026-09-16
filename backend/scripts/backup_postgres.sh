#!/usr/bin/env bash
set -euo pipefail
: "${DATABASE_URL:?DATABASE_URL required}"
mkdir -p "${BACKUP_DIR:-./backups}"
f="${BACKUP_DIR:-./backups}/agrici-$(date -u +%Y%m%dT%H%M%SZ).dump"
pg_dump --format=custom --no-owner --no-acl "$DATABASE_URL" > "$f"
echo "$f"
