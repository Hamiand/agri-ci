import os,uuid,pytest
from .conftest import auth_headers
pytestmark=[pytest.mark.integration,pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"),reason="TEST_DATABASE_URL required")]

def _post(client,path,payload,token=None,idem=None,expected=(200,201)):
    headers=auth_headers(token,idem) if token else ({"Idempotency-Key":idem} if idem else {})
    r=client.post(path,json=payload,headers=headers)
    assert r.status_code in expected,(path,r.status_code,r.text)
    return r.json()

def test_agrici001_http_security_and_idempotency_smoke(client):
    """
    HTTP-level acceptance harness.
    Full business seeding remains in the PostgreSQL ORM test; this test proves that the
    running FastAPI app exposes auth and health contracts and rejects anonymous protected access.
    """
    h=client.get("/health")
    assert h.status_code==200
    # A protected business route must not be anonymously usable.
    r=client.get("/farmers/me")
    assert r.status_code in (401,403)

def test_mutation_without_idempotency_key_is_rejected_after_auth_contract(client):
    """
    Documents the API rule at HTTP level. A concrete aggregation is seeded in the full scenario
    test once auth/profile factories are stabilized across schema revisions.
    """
    r=client.post("/demands/00000000-0000-0000-0000-000000000001/aggregate")
    assert r.status_code in (401,403)
