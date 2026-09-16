import os
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://x:x@localhost/x")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET", "test-secret-that-is-long-enough-for-tests")

from app.core.security import hash_password, verify_password

def test_password_hashing():
    raw = "A-strong-test-password"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed)
    assert not verify_password("wrong-password", hashed)
