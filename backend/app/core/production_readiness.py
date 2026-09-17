import os
from urllib.parse import urlparse

_PLACEHOLDER_SECRETS = {"change-me", "ci-only-secret-change-me"}


def _strong_secret(name: str, minimum: int = 32) -> bool:
    value = os.getenv(name, "").strip()
    return bool(value) and value not in _PLACEHOLDER_SECRETS and len(value) >= minimum


def _production_database_url() -> bool:
    value = os.getenv("DATABASE_URL", "").strip()
    return value.startswith(("postgresql://", "postgresql+psycopg://"))


def _safe_cors_origins() -> bool:
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if not raw:
        return False
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    if not origins or "*" in origins:
        return False
    return all(urlparse(origin).scheme == "https" and bool(urlparse(origin).netloc) for origin in origins)


def production_checks():
    env = os.getenv("APP_ENV", "development").strip().lower()
    checks = {
        "database_url": _production_database_url(),
        "jwt_secret": _strong_secret("JWT_SECRET"),
        "payment_webhook_secret": _strong_secret("PAYMENT_WEBHOOK_SECRET"),
        "cors_origins": _safe_cors_origins(),
        "production_environment": env in ("staging", "production"),
    }
    return checks, all(checks.values())
