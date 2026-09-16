import hashlib,hmac,os
from app.payments.webhook import valid_signature
def test_webhook_signature(monkeypatch):
    monkeypatch.setenv("PAYMENT_WEBHOOK_SECRET","secret")
    raw=b'{"event":"payment.success"}'
    sig=hmac.new(b"secret",raw,hashlib.sha256).hexdigest()
    assert valid_signature(raw,sig)
    assert not valid_signature(raw,"bad")
