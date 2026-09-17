from app.core.production_readiness import production_checks


def _valid_env(monkeypatch):
    monkeypatch.setenv("APP_ENV","staging")
    monkeypatch.setenv("DATABASE_URL","postgresql://agrici:secret@db/agrici")
    monkeypatch.setenv("JWT_SECRET","j"*48)
    monkeypatch.setenv("PAYMENT_WEBHOOK_SECRET","w"*48)
    monkeypatch.setenv("CORS_ORIGINS","https://pilot.agri-ci.example")


def test_production_readiness_accepts_safe_pilot_configuration(monkeypatch):
    _valid_env(monkeypatch)
    checks,ready=production_checks()
    assert ready is True
    assert all(checks.values())


def test_production_readiness_rejects_wildcard_or_http_cors(monkeypatch):
    _valid_env(monkeypatch)
    monkeypatch.setenv("CORS_ORIGINS","*")
    checks,ready=production_checks()
    assert ready is False and checks["cors_origins"] is False

    monkeypatch.setenv("CORS_ORIGINS","http://pilot.agri-ci.example")
    checks,ready=production_checks()
    assert ready is False and checks["cors_origins"] is False


def test_production_readiness_rejects_weak_secrets_and_non_postgres(monkeypatch):
    _valid_env(monkeypatch)
    monkeypatch.setenv("JWT_SECRET","too-short")
    monkeypatch.setenv("PAYMENT_WEBHOOK_SECRET","change-me")
    monkeypatch.setenv("DATABASE_URL","sqlite:///pilot.db")
    checks,ready=production_checks()
    assert ready is False
    assert checks["jwt_secret"] is False
    assert checks["payment_webhook_secret"] is False
    assert checks["database_url"] is False
