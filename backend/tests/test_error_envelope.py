from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _assert_error_envelope(response, code):
    body = response.json()
    assert body["detail"] == code
    assert body["error"]["code"] == code
    assert isinstance(body["error"]["message"], str)
    assert isinstance(body["error"]["details"], dict)
    assert body["error"]["trace_id"] == response.headers["X-Request-ID"]


def test_route_http_errors_use_canonical_envelope_and_request_id():
    response = client.get("/definitely-not-an-agrici-route", headers={"X-Request-ID": "trace-http-404"})
    assert response.status_code == 404
    _assert_error_envelope(response, "Not Found")
    assert response.headers["X-Request-ID"] == "trace-http-404"


def test_validation_errors_use_canonical_envelope_without_echoing_input():
    secret_like_value = "do-not-echo-this-value"
    response = client.post(
        "/auth/login",
        json={"phone": secret_like_value},
        headers={"X-Request-ID": "trace-validation-422"},
    )
    assert response.status_code == 422
    _assert_error_envelope(response, "VALIDATION_ERROR")
    assert response.headers["X-Request-ID"] == "trace-validation-422"
    assert "fields" in response.json()["error"]["details"]
    assert secret_like_value not in response.text
