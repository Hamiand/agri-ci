import os, uuid, pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL required"),
]


def test_register_login_refresh_and_protected_farmer_route(app_client):
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
    login_body = login.json()
    access_token = login_body.get("access_token")
    refresh_token = login_body.get("refresh_token")
    assert access_token, login_body
    assert refresh_token, login_body
    assert access_token != refresh_token

    unauth = client.get("/farmers/me")
    assert unauth.status_code in (401, 403)

    auth = client.get("/farmers/me", headers={"Authorization": f"Bearer {access_token}"})
    # A missing farmer profile is acceptable here; a valid access token is not.
    assert auth.status_code not in (401, 403), auth.text

    # A refresh token must never authenticate a protected business endpoint.
    refresh_as_access = client.get(
        "/farmers/me", headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert refresh_as_access.status_code in (401, 403), refresh_as_access.text

    rotated = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert rotated.status_code == 200, rotated.text
    rotated_body = rotated.json()
    new_access = rotated_body.get("access_token")
    new_refresh = rotated_body.get("refresh_token")
    assert new_access, rotated_body
    assert new_refresh, rotated_body
    assert new_access != new_refresh

    refreshed_auth = client.get(
        "/farmers/me", headers={"Authorization": f"Bearer {new_access}"}
    )
    assert refreshed_auth.status_code not in (401, 403), refreshed_auth.text

    refreshed_refresh_as_access = client.get(
        "/farmers/me", headers={"Authorization": f"Bearer {new_refresh}"}
    )
    assert refreshed_refresh_as_access.status_code in (401, 403), refreshed_refresh_as_access.text
