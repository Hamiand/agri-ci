# v0.27 Local Checks

## compileall
Exit: 0
```text
Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/spreadsheet_warmup.py", line 772, in warm_spreadsheet_runtime
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/rpc/connection.py", line 37, in get_or_create_client
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/rpc/daemon.py", line 124, in start_daemon
TimeoutError: Timed out waiting for artifact tool daemon socket. Set ARTIFACT_TOOL_RPC_DAEMON_STARTUP_TIMEOUT_S=<seconds> to increase the limit.

```

## commercial_gate
Exit: 0
```text
PASS commercial_gate_doc
PASS rbac_matrix
PASS mutation_matrix
PASS payment_webhook
PASS postgres_ci
PASS agrici001_manifest
PASS concurrency_test
PASS http_e2e_harness

```

## shell_syntax
Exit: 0
```text

```

## module_audit
Exit: 0
```text
OK      fastapi 0.128.2
OK      sqlalchemy 2.0.50
OK      alembic 1.18.4
OK      pydantic 2.13.4
OK      pytest 9.0.2
OK      httpx 0.28.1
OK      jwt 2.13.0
MISSING pwdlib No module named 'pwdlib'
MISSING redis No module named 'redis'
MISSING psycopg No module named 'psycopg'

```

