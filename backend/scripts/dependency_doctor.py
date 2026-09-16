import importlib,sys
required={
 "fastapi":"fastapi","sqlalchemy":"sqlalchemy","alembic":"alembic","pydantic":"pydantic",
 "pydantic_settings":"pydantic-settings","jwt":"PyJWT","pwdlib":"pwdlib[argon2]",
 "redis":"redis","psycopg":"psycopg[binary]","pytest":"pytest","httpx":"httpx",
}
missing=[]
for module,package in required.items():
    try:
        m=importlib.import_module(module)
        print("OK     ",package,getattr(m,"__version__",""))
    except Exception as e:
        print("MISSING",package,repr(e));missing.append(package)
if missing:
    print("\nInstall missing packages with:")
    print("python -m pip install "+" ".join(repr(x) for x in missing))
    raise SystemExit(1)
