from pathlib import Path
root=Path(__file__).parents[2]
software={
 "PostgreSQL CI workflow":root/".github/workflows/backend-ci.yml",
 "Concurrency race test":root/"backend/tests/integration/test_offer_locking_postgres.py",
 "Idempotency replay DB test":root/"backend/tests/integration/test_idempotency_postgres.py",
 "HTTP E2E harness":root/"backend/tests/integration/test_agrici001_http_e2e.py",
 "Commercial route inventory":root/"backend/tests/test_commercial_route_inventory.py",
 "Signed payment webhook":root/"backend/app/payments/webhook.py",
 "Pilot runbook":root/"docs/PILOT-RUNBOOK.md",
}
for name,p in software.items():print(("READY" if p.exists() else "MISSING"),name)
print("\nNOTE: artifact presence is not runtime test success. GitHub/PostgreSQL CI must be green.")
