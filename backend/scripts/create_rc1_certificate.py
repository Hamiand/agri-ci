import json,datetime
from pathlib import Path
e=Path(".rc1-evidence")
required=["postgres_migrations.green","concurrency.green","idempotency.green","http_e2e.green"]
missing=[x for x in required if not (e/x).exists()]
if missing:
    raise SystemExit("Cannot create RC1 certificate; missing: "+", ".join(missing))
meta={}
if (e/"metadata.json").exists():meta=json.loads((e/"metadata.json").read_text())
cert={
 "product":"AGRI-CI",
 "release":"1.0 Commercial Pilot RC1",
 "software_runtime_gate":"PASSED",
 "issued_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "evidence":required,
 "metadata":meta,
 "scope_note":"Software runtime gate only; external payment certification, hosting/TLS, backup restore, monitoring, legal/privacy and field-operations gates remain separate."
}
(e/"RC1-CERTIFICATE.json").write_text(json.dumps(cert,indent=2))
print(json.dumps(cert,indent=2))
