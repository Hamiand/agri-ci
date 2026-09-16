from app.core.idempotency import request_hash
def test_request_hash_stable_across_key_order():
    assert request_hash({"b":2,"a":1}) == request_hash({"a":1,"b":2})
def test_request_hash_changes_with_payload():
    assert request_hash({"a":1}) != request_hash({"a":2})
