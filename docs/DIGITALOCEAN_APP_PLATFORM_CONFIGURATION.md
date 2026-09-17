# AGRI-CI — DigitalOcean App Platform configuration worksheet

This is a preparation worksheet, not a deployment credential file. Do not put passwords, API tokens or production secrets in this document.

DigitalOcean App Platform supports GitHub sources, Dockerfile builds, component health checks, workers and PRE_DEPLOY jobs. Final resource sizes and managed-service connection values are chosen only after the DigitalOcean account is authorized.

## Component 1 — API service

- Name: `agrci-api`
- GitHub repository: `Hamiand/agri-ci`
- Production branch after approval: `main`
- Preparation branch: `deployment/digitalocean-prep`
- Source/build context: `backend`
- Dockerfile: `backend/Dockerfile`
- HTTP port: `8000`
- Health check path: `/health`
- Instance count for initial pilot: `1` until measured load justifies scaling
- Required runtime environment: see `backend/.env.production.example`

Do not use `/ready` as the liveness probe because it intentionally depends on PostgreSQL. Use `/ready` as a deployment/readiness verification.

## Component 2 — Web service

- Name: `agrci-web`
- GitHub repository: `Hamiand/agri-ci`
- Source/build context: `web`
- Dockerfile: `web/Dockerfile`
- HTTP port: `3000`
- Build-time variable: `NEXT_PUBLIC_API_BASE_URL=https://api.agri-ci.com`

The API base URL contains no secret. It must match the canonical Release 1.0 route contract, which currently exposes endpoints at the API root.

## Component 3 — Transactional-outbox worker

- Name: `agrci-outbox-worker`
- Source/build context: `backend`
- Dockerfile: `backend/Dockerfile`
- Override run command: `python -m app.events.worker`
- No public HTTP route
- Same PostgreSQL environment as the API

The current worker is retry-safe and persists publish attempts, but its `publish_event` function remains an adapter seam. A real downstream messaging/notification integration is a separate production decision.

## Component 4 — Alembic pre-deploy job

- Name: `agrci-migrate`
- Kind: `PRE_DEPLOY`
- Source/build context: `backend`
- Dockerfile: `backend/Dockerfile`
- Run command: `alembic upgrade head`
- Same `DATABASE_URL` as the API

A failed migration must fail the deployment. Do not run competing migrations independently in every API instance.

## Managed PostgreSQL

Required characteristics for the real pilot:

- managed PostgreSQL compatible with the repository's PostgreSQL-specific UUID/JSONB models;
- encrypted connection;
- automated backups;
- documented retention;
- a tested restore procedure before real commercial transactions;
- database not exposed as a public application endpoint.

The repository already proves Alembic migrations and PostgreSQL integration/concurrency behavior in CI. Production provisioning remains external evidence.

## Redis-compatible service

`REDIS_URL` remains part of the backend configuration contract. Provision the final service only when the DigitalOcean environment is created. Prefer a private/trusted connection where supported.

## Secrets entered in DigitalOcean, not GitHub

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `PAYMENT_WEBHOOK_SECRET`
- future licensed-payment-provider credentials

## Public/non-secret settings

- `APP_ENV=production`
- `APP_DEBUG=false`
- `JWT_ALGORITHM=HS256`
- `JWT_ACCESS_TOKEN_MINUTES=30`
- `JWT_REFRESH_TOKEN_DAYS=30`
- `CORS_ORIGINS=https://www.agri-ci.com`
- `NEXT_PUBLIC_API_BASE_URL=https://api.agri-ci.com`

## Domains

Planned only; do not change DNS yet:

- `www.agri-ci.com` → web
- `api.agri-ci.com` → API

The registrar can remain separate from DigitalOcean.

## Required checks before enabling real pilot traffic

1. GitHub CI green on the exact deployment revision, including production Docker image builds.
2. Alembic PRE_DEPLOY migration succeeds.
3. `/health` returns HTTP 200.
4. `/ready` returns HTTP 200 with the managed PostgreSQL connection.
5. `/commercial-readiness` returns HTTP 200 only with the intended production configuration.
6. HTTPS is valid for both public hostnames.
7. CORS allows the intended web origin and never uses `*`.
8. Generic test payment webhook remains unavailable in production.
9. Backup exists and restoration has been tested.
10. Licensed payment provider, legal/privacy review, real pilot actors and controlled field rehearsal have independent evidence.
