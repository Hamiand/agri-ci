# AGRI-CI — DigitalOcean deployment plan

Status: preparation only. No paid DigitalOcean resource is created by this document.

## Target topology

- Web: Next.js service from `web/`, public HTTPS endpoint.
- API: FastAPI/Uvicorn service from `backend/`, public HTTPS endpoint.
- Database: DigitalOcean Managed PostgreSQL, private/trusted connection where supported.
- Redis: managed Redis-compatible service/private connection.
- Worker: `python -m app.events.worker`, using the same backend image and database environment.
- Payment: external licensed provider; the generic/test webhook remains disabled in production.

## Suggested public endpoints

- `https://www.agri-ci.com` — web application
- `https://api.agri-ci.com` — API

The domain may remain registered elsewhere. DNS should point to DigitalOcean only after the pilot environment is ready.

## Canonical API contract

Release 1.0 currently exposes its API routes at the API root. Do not append `/api/v1` unless the backend contract is deliberately versioned in a later release.

Therefore the production web build variable is:

- `NEXT_PUBLIC_API_BASE_URL=https://api.agri-ci.com`

This value is public by design and is compiled into the Next.js web build.

## Required backend environment variables

Never commit real secret values to Git.

- `APP_ENV=production`
- `APP_DEBUG=false`
- `DATABASE_URL=<managed PostgreSQL connection string>`
- `REDIS_URL=<managed Redis connection string>`
- `JWT_SECRET=<random secret, at least 32 characters>`
- `JWT_ALGORITHM=HS256`
- `JWT_ACCESS_TOKEN_MINUTES=30`
- `JWT_REFRESH_TOKEN_DAYS=30`
- `CORS_ORIGINS=https://www.agri-ci.com`
- `PAYMENT_WEBHOOK_SECRET=<strong deployment secret>`

The current production-readiness gate requires `PAYMENT_WEBHOOK_SECRET`, although the generic webhook endpoint itself is disabled when `APP_ENV=production`. A provider-specific production adapter and provider-specific secrets must only be added after a licensed provider is selected.

## Build/run configuration

### API

- Source directory/build context: `backend/`
- Dockerfile: `backend/Dockerfile`
- Runtime: Uvicorn on port 8000
- Liveness endpoint: `/health`
- Database readiness endpoint: `/ready`
- Commercial readiness endpoint: `/commercial-readiness`

### Web

- Source directory/build context: `web/`
- Dockerfile: `web/Dockerfile`
- Build argument: `NEXT_PUBLIC_API_BASE_URL`
- Runtime port: 3000

### Worker

The repository contains a retry-safe transactional-outbox worker at `app.events.worker`. For the pilot it should run as a separate worker component using the backend image and the command:

```sh
python -m app.events.worker
```

Its current publishing adapter is still a seam for a real downstream notification/event adapter. Do not interpret successful worker execution as proof that an external messaging integration has been completed.

## Database migrations

Alembic migrations must be applied against managed PostgreSQL before a new API revision receives pilot traffic. Migration failure is a deployment failure; do not manually modify production tables to bypass it.

Recommended pre-deploy command from the backend image:

```sh
alembic upgrade head
```

DigitalOcean App Platform supports pre-deploy jobs, so the final app configuration should run this migration as a PRE_DEPLOY job rather than racing migrations inside multiple API instances.

## Health checks

Use `/health` for service liveness because it does not require a database round trip. Use `/ready` during deployment/smoke verification to prove that PostgreSQL is reachable. `/commercial-readiness` additionally checks the production configuration gate.

## Production gate

Before real transactions, verify all required production checks:

- PostgreSQL production URL
- strong JWT secret
- strong deployment/payment webhook secret
- explicit HTTPS CORS origins (never `*`)
- `APP_ENV=production`

A green software gate does not prove external readiness.

## CI deployment proof

CI must build both production Dockerfiles in addition to the existing Next.js build, backend tests, PostgreSQL integration/concurrency tests, Alembic migration proof and RC1 runtime evidence. This prevents an application build from passing while a production container is broken.

## External go-live evidence still required

- DigitalOcean account/resource authorization and billing
- production PostgreSQL and Redis provisioning
- backup/restore validation
- DNS and HTTPS validation
- monitoring/alerts
- licensed payment provider selection and certification
- legal/privacy validation
- named real pilot participants
- controlled field rehearsal

## Deployment sequence

1. Keep preparation changes isolated on `deployment/digitalocean-prep`.
2. Build/test API and web production containers in CI.
3. Keep Pull Request #2 in draft until all deployment checks pass.
4. Only then create/authorize DigitalOcean resources.
5. Provision managed PostgreSQL and Redis.
6. Enter secrets in DigitalOcean, never in GitHub source files.
7. Run Alembic as a pre-deploy job.
8. Deploy API and worker.
9. Deploy web with the final API root URL as its build variable.
10. Verify `/health`, `/ready`, authentication, CORS, RBAC, idempotency and a controlled transaction smoke test.
11. Configure DNS/HTTPS.
12. Verify backups and restoration procedure.
13. Integrate/certify the selected licensed payment provider.
14. Execute the controlled field rehearsal before real-money pilot transactions.
