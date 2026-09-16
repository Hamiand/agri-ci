import os, uuid, pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL required"),
]


def _register_and_login(client, role):
    suffix = uuid.uuid4().hex[:8]
    phone = f"+22507{suffix}"
    password = "Pilot-Test-Password-123!"
    reg = client.post("/auth/register", json={
        "phone": phone,
        "password": password,
        "preferred_language": "fr",
        "role": role,
    })
    assert reg.status_code in (200, 201), reg.text
    login = client.post("/auth/login", json={"phone": phone, "password": password})
    assert login.status_code == 200, login.text
    return reg.json()["id"], {"Authorization": f"Bearer {login.json()['access_token']}"}


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
    assert auth.status_code not in (401, 403), auth.text

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


def test_transporter_cannot_create_lots_or_transport_jobs_over_http(app_client):
    client = app_client
    transporter_id, headers = _register_and_login(client, "TRANSPORTER")
    fake_order = str(uuid.uuid4())

    lot = client.post(
        "/lots",
        headers={**headers, "Idempotency-Key": f"forbidden-lot-{uuid.uuid4().hex}"},
        json={"order_id": fake_order, "quality_check_ids": [str(uuid.uuid4())]},
    )
    assert lot.status_code == 403, lot.text

    transport = client.post(
        "/transport-jobs",
        headers={**headers, "Idempotency-Key": f"forbidden-job-{uuid.uuid4().hex}"},
        json={
            "order_id": fake_order,
            "lot_ids": [str(uuid.uuid4())],
            "transporter_user_id": transporter_id,
            "origin": "Village pilote",
            "destination": "Abidjan",
            "vehicle_ref": "TEST-TRUCK",
            "driver_name": "Test Driver",
        },
    )
    assert transport.status_code == 403, transport.text
