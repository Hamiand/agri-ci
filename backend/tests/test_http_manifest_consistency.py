import json
from pathlib import Path
from app.main import app
ROOT=Path(__file__).parents[2]
def norm(path):
    # parameter names are semantically irrelevant for manifest-to-route matching
    import re
    return re.sub(r"\{[^}]+\}","{}",path)
def test_canonical_http_flow_paths_are_mounted():
    flow=json.loads((ROOT/"docs/agrici-001-http-flow.json").read_text())
    mounted={(m,norm(r.path)) for r in app.routes for m in (getattr(r,"methods",None) or set())}
    missing=[]
    for step in flow["steps"]:
        item=(step["method"],norm(step["path"]))
        if item not in mounted:missing.append(item)
    assert not missing,f"Manifest references missing routes: {missing}"
