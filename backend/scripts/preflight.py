import os
from urllib.parse import urlparse

bad=[]

def fail(name):
    bad.append(name)


database_url=os.getenv("DATABASE_URL","").strip()
if not database_url.startswith(("postgresql://","postgresql+psycopg://")):
    fail("DATABASE_URL")

for key in ("JWT_SECRET","PAYMENT_WEBHOOK_SECRET"):
    value=os.getenv(key,"").strip()
    if not value or value in {"change-me","ci-only-secret-change-me"} or len(value)<32:
        fail(key)

cors_raw=os.getenv("CORS_ORIGINS","").strip()
origins=[item.strip() for item in cors_raw.split(",") if item.strip()]
if not origins or "*" in origins or any(urlparse(origin).scheme!="https" or not urlparse(origin).netloc for origin in origins):
    fail("CORS_ORIGINS")

if os.getenv("APP_ENV","").strip().lower() not in {"staging","production"}:
    fail("APP_ENV")

if bad:
    print("PREFLIGHT FAILED:",", ".join(sorted(set(bad))))
    raise SystemExit(1)
print("PREFLIGHT PASS")
