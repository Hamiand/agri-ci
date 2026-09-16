from pathlib import Path
ROOT=Path(__file__).parents[2]
def test_ci_has_executable_rc1_runtime_job():
    s=(ROOT/".github/workflows/backend-ci.yml").read_text()
    assert "rc1-runtime-proof:" in s
    assert "postgres:16" in s
    assert "bash scripts/collect_rc1_evidence.sh" in s
    assert "python scripts/rc1_gate.py" in s
    assert "actions/upload-artifact@v4" in s
def test_evidence_collector_removes_stale_proof():
    s=(ROOT/"backend/scripts/collect_rc1_evidence.sh").read_text()
    assert "rm -rf .rc1-evidence" in s
