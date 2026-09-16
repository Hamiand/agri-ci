import os,uuid,pytest
from fastapi.testclient import TestClient

pytestmark=[
 pytest.mark.integration,
 pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"),reason="TEST_DATABASE_URL required"),
]

def test_register_login_and_protected_farmer_route(app_client):
    client=app_client
    suffix=uuid.uuid4().hex[:10]
    email=f"http-{suffix}@agrici.test"
    password="Pilot-Test-Password-123!"
    reg=client.post("/auth/register",json={"email":email,"password":password,"full_name":"AGRI-CI HTTP Pilot"})
    assert reg.status_code in (200,201),reg.text
    login=client.post("/auth/login",json={"email":email,"password":password})
    assert login.status_code==200,login.text
    body=login.json()
    token=body.get("access_token")
    assert token,body
    unauth=client.get("/farmers/me")
    assert unauth.status_code in (401,403)
    auth=client.get("/farmers/me",headers={"Authorization":f"Bearer {token}"})
    # No farmer profile yet is acceptable; authentication itself must not be rejected.
    assert auth.status_code not in (401,403),auth.text
