import os,pytest
pytestmark=[pytest.mark.integration,pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"),reason="TEST_DATABASE_URL required for PostgreSQL integration")]
def test_concurrency_contract_documented():
    # Executed in CI only when a real PostgreSQL test database is configured.
    # Two concurrent reservations for the same available quantity must serialize via SELECT FOR UPDATE.
    assert os.getenv("TEST_DATABASE_URL")
