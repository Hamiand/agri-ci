import os, uuid, pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL required"),
]


def test_register_login_and_protected_farmer_route(app_client):
    client = app_client
    suffix = uuid.uuid4().hex[:8]
    phone = f"+22507{suffix}"
    password = "Pilot-Test-Password-123!"

    reg = client.post("/auth/register", json={
        "phone": phone,
        "password": password,
        "preferred_language": "fr",
        "role": "FARMER",
    })
    assert reg.status_code in (200, 201), reg.text

    login = client.post("/auth/login", json={"phone": phone, "password": password})
    assert login.status_code == 200, login.text
    token = login.json().get("access_token")
    assert token, login.json()

    unauth = client.get("/farmers/me")
    assert unauth.status_code in (401, 403)
    auth = client.get("/farmers/me", headers={"Authorization": f"Bearer {token}"})
    # A missing farmer profile is acceptable here; a valid access token is not.
    assert auth.status_code not in (401, 403), auth.text
