from pathlib import Path
ROOT=Path(__file__).parents[2]
def test_manual_provider_success_is_disabled_in_production_source_contract():
    s=(ROOT/"backend/app/payments/router.py").read_text()
    assert 'APP_ENV' in s
    assert '== "production"' in s
    assert 'detail="NOT_FOUND"' in s
def test_signed_webhook_remains_present():
    s=(ROOT/"backend/app/payments/webhook.py").read_text()
    assert "X-Signature" in s or "x-signature" in s.lower()
    assert "PAYMENT_WEBHOOK_SECRET" in s
