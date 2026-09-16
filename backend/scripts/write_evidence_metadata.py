import json,os,subprocess,datetime
from pathlib import Path
def git(*args):
    try:return subprocess.check_output(["git",*args],text=True).strip()
    except Exception:return "unknown"
p=Path(".rc1-evidence");p.mkdir(exist_ok=True)
data={
 "generated_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "git_commit":os.getenv("GITHUB_SHA") or git("rev-parse","HEAD"),
 "github_run_id":os.getenv("GITHUB_RUN_ID","local"),
 "database_url_present":bool(os.getenv("DATABASE_URL")),
 "test_database_url_present":bool(os.getenv("TEST_DATABASE_URL")),
}
(p/"metadata.json").write_text(json.dumps(data,indent=2))
print(json.dumps(data,indent=2))
