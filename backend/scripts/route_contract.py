from app.main import app
for r in sorted(app.routes,key=lambda x:(x.path,sorted(getattr(x,"methods",[]) or []))):
    if r.path.startswith("/openapi") or r.path.startswith("/docs") or r.path.startswith("/redoc"):continue
    print(f"{','.join(sorted(getattr(r,'methods',[]) or [])):18} {r.path}")
