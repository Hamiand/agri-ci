import importlib
mods=["fastapi","sqlalchemy","alembic","pydantic","pytest","httpx","jwt","pwdlib","redis","psycopg"]
for m in mods:
    try:
        x=importlib.import_module(m);print(f"OK      {m} {getattr(x,'__version__','')}")
    except Exception as e:print(f"MISSING {m} {e}")
