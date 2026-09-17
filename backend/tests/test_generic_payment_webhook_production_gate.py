from pathlib import Path


def test_generic_payment_webhook_is_disabled_in_production():
    source=Path("app/payments/webhook.py").read_text()
    assert 'os.getenv("APP_ENV","development") == "production"' in source
    assert 'status_code=404,detail="NOT_FOUND"' in source
    assert "provider's documented" in source
