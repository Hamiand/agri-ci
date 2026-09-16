import hashlib, json
def request_hash(payload: dict) -> str:
    canonical=json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()
    return hashlib.sha256(canonical).hexdigest()
