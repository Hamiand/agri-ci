import os,sys
required=["DATABASE_URL","JWT_SECRET","PAYMENT_WEBHOOK_SECRET","CORS_ORIGINS"]
bad=[]
for k in required:
    v=os.getenv(k,"").strip()
    if not v or v in {"change-me","ci-only-secret-change-me"}:bad.append(k)
if os.getenv("APP_ENV") not in {"staging","production"}:bad.append("APP_ENV")
if bad:
    print("PREFLIGHT FAILED:",", ".join(sorted(set(bad))))
    raise SystemExit(1)
print("PREFLIGHT PASS")
