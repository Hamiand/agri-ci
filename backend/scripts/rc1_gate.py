import os
from pathlib import Path
e=Path(".rc1-evidence")
checks={
 "PostgreSQL/Alembic": e/"postgres_migrations.green",
 "offer concurrency": e/"concurrency.green",
 "idempotency replay": e/"idempotency.green",
 "authenticated AGRI-CI-001 HTTP E2E": e/"http_e2e.green",
}
failed=[]
for label,path in checks.items():
    ok=path.exists()
    print(("PASS" if ok else "BLOCK"),label)
    if not ok:failed.append(label)
if failed:
    print("\nRC1 BLOCKED:",", ".join(failed))
    raise SystemExit(1)
print("\nAGRI-CI SOFTWARE RC1 GATE PASSED")
