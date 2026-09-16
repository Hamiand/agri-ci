# AGRI-CI v0.30 Status

v0.30 converts the RC1 gate from manually supplied environment flags to filesystem evidence
created only after the corresponding runtime command succeeds.

It also derives an HTTP contract inventory directly from the repository's router and schema
source files and adds an authenticated register/login/protected-route PostgreSQL HTTP test.

This is an important distinction:
- route presence is a contract proof;
- authentication through TestClient is an HTTP runtime proof;
- AGRI-CI-001 remains a full business E2E proof and must not be marked green until its
  database-backed test succeeds.

The sandbox still lacks PostgreSQL/Docker and some runtime dependencies, so no RC1 evidence
files are pre-created in this package.
