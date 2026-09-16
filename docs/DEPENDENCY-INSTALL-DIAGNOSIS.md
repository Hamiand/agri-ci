# v0.26 Dependency Installation Diagnosis

The local editable installation failed during pip's **isolated build-dependency environment**
creation, before AGRI-CI application dependencies were installed.

The host Python environment was inspected separately:
- already present: FastAPI, SQLAlchemy, Alembic, Pydantic, PyJWT, pytest, httpx;
- missing locally: pwdlib, redis, psycopg.

This does not indicate an AGRI-CI source-code failure. It means the current sandbox cannot
complete the dependency bootstrap required for a faithful application runtime.

## v0.27 correction
CI/staging now:
1. upgrades pip/setuptools/wheel;
2. installs a pinned-purpose `requirements.txt`;
3. installs AGRI-CI editable with `--no-build-isolation`;
4. runs `dependency_doctor.py`;
5. then executes Alembic/application/tests.

GitHub Actions remains the intended proof environment because it has network package access
and a PostgreSQL service.
