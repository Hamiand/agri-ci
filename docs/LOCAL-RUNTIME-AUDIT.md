# AGRI-CI v0.26 Local Runtime Audit

This report records what was actually executed in the current environment.

## Infrastructure availability
- docker: `NOT AVAILABLE`
- podman: `NOT AVAILABLE`
- psql: `NOT AVAILABLE`
- postgres: `NOT AVAILABLE`

## Executed checks
### compileall
- exit code: **0**
```text
Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/spreadsheet_warmup.py", line 772, in warm_spreadsheet_runtime
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/rpc/connection.py", line 37, in get_or_create_client
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/rpc/daemon.py", line 124, in start_daemon
TimeoutError: Timed out waiting for artifact tool daemon socket. Set ARTIFACT_TOOL_RPC_DAEMON_STARTUP_TIMEOUT_S=<seconds> to increase the limit.

```

### commercial_gate
- exit code: **0**
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

### shell_syntax
- exit code: **0**
```text
(no output)
```

### pip_install_editable
- exit code: **1**
```text
Obtaining file:///mnt/data/agri-ci-v0.26-local-runtime-audit/backend
  Installing build dependencies: started
  Installing build dependencies: finished with status 'error'

```
