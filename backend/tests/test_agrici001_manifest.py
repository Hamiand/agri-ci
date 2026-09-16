import json
from pathlib import Path
def test_agrici001_manifest_invariants():
    p=Path(__file__).parents[2]/"docs/agrici-001.json"
    d=json.loads(p.read_text())
    assert sum(x["kg"] for x in d["initial_allocation"])==3000
    assert 3000-d["decline"]["kg"]+d["replacement"]["kg"]==3000
    q=d["physical_reference"]
    assert sum(q["grades"].values())==q["received_kg"]
    pay=d["payment_reference"]
    assert pay["gross_xof"]-pay["transport_xof"]-pay["service_xof"]-pay["other_xof"]==pay["net_xof"]
