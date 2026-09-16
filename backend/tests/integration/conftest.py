import os,pytest
@pytest.fixture
def app_client(monkeypatch):
    url=os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL required")
    monkeypatch.setenv("DATABASE_URL",url)
    # Import after DATABASE_URL is selected.
    from app.main import app
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        yield client
