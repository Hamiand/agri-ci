from pathlib import Path
ROOT=Path(__file__).parents[2]
def test_production_compose_has_healthcheck():
    s=(ROOT/"docker-compose.production.yml").read_text()
    assert "healthcheck:" in s and "/health" in s
def test_cors_is_environment_driven_and_not_wildcard():
    s=(ROOT/"backend/app/main.py").read_text()
    assert "CORS_ORIGINS" in s
    assert 'allow_origins=["*"]' not in s
def test_preflight_requires_commercial_secrets():
    s=(ROOT/"backend/scripts/preflight.py").read_text()
    for k in ["DATABASE_URL","JWT_SECRET","PAYMENT_WEBHOOK_SECRET","CORS_ORIGINS"]:
        assert k in s
def test_editable_build_metadata_exists():
    s=(ROOT/"backend/pyproject.toml").read_text()
    assert "[build-system]" in s and "setuptools.build_meta" in s
