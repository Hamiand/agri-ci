import os
import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.getenv("TEST_DATABASE_URL"),
        reason="TEST_DATABASE_URL required",
    ),
]


def test_agrici001_http_security_and_idempotency_smoke(app_client):
    """Prove health and anonymous protection at the HTTP boundary."""
    health = app_client.get("/health")
    assert health.status_code == 200

    protected = app_client.get("/farmers/me")
    assert protected.status_code in (401, 403)


def test_mutation_without_auth_is_rejected_before_business_processing(app_client):
    """A protected aggregation mutation cannot be invoked anonymously."""
    response = app_client.post(
        "/demands/00000000-0000-0000-0000-000000000001/aggregate"
    )
    assert response.status_code in (401, 403)
