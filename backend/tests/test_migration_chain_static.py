import re
from pathlib import Path
def test_migration_chain_has_one_head_and_no_duplicate_revisions():
    d=Path(__file__).parents[1]/"migrations/versions"
    rows=[]
    for p in d.glob("*.py"):
        s=p.read_text()
        r=re.search(r'revision\s*=\s*["\']([^"\']+)',s)
        dn=re.search(r'down_revision\s*=\s*(?:["\']([^"\']+)["\']|None)',s)
        if r: rows.append((p.name,r.group(1),dn.group(1) if dn else None))
    revs=[r for _,r,_ in rows]
    assert len(revs)==len(set(revs)),"duplicate Alembic revision"
    parents={dn for _,_,dn in rows if dn}
    heads=set(revs)-parents
    assert len(heads)==1,f"Expected one Alembic head, got {heads}"
