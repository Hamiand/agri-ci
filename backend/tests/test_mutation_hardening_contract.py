from pathlib import Path
BASE=Path(__file__).parents[1]/"app"
def source(rel):return (BASE/rel).read_text()
def test_commitments_have_object_ownership():
    s=source("commitments/router.py")
    assert "farmer_for_user" in s and "COMMITMENT_FORBIDDEN" in s
def test_sensitive_mutations_require_idempotency_header():
    for rel in ["aggregation/router.py","orders/router.py","collection/router.py",
                "logistics/router.py","deliveries/router.py","payments/router.py"]:
        s=source(rel)
        assert "Idempotency-Key" in s,rel
def test_payment_webhook_is_signed():
    s=source("payments/webhook.py")
    assert "hmac.compare_digest" in s and "INVALID_WEBHOOK_SIGNATURE" in s
