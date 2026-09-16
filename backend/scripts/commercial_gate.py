from pathlib import Path
root=Path(__file__).parents[2]
checks={
 "commercial_gate_doc":(root/"docs/COMMERCIAL-PILOT-GATE.md").exists(),
 "rbac_matrix":(root/"docs/RBAC-MATRIX.md").exists(),
 "mutation_matrix":(root/"docs/MUTATION-HARDENING-MATRIX.md").exists(),
 "payment_webhook":(root/"backend/app/payments/webhook.py").exists(),
 "postgres_ci":(root/".github/workflows/backend-ci.yml").exists(),
 "agrici001_manifest":(root/"docs/agrici-001.json").exists(),
 "concurrency_test":(root/"backend/tests/integration/test_offer_locking_postgres.py").exists(),
 "http_e2e_harness":(root/"backend/tests/integration/test_agrici001_http_e2e.py").exists(),
}
for k,v in checks.items():print(f"{'PASS' if v else 'FAIL':4} {k}")
raise SystemExit(0 if all(checks.values()) else 1)
