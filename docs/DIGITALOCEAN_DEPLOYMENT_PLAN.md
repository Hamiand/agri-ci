# AGRI-CI — DigitalOcean deployment plan

Status: preparation only. No paid DigitalOcean resource is created by this document.

## Target topology

- Web: Next.js service from `web/`, public HTTPS endpoint.
- API: FastAPI/Uvicorn service from `backend/`, public HTTPS endpoint.
- Database: DigitalOcean Managed PostgreSQL, private/trusted connection where supported.
- Redis: managed Redis-compatible service/private connection.
- Worker: background worker service when the transactional outbox worker is enabled for the pilot.
- Payment: external licensed provider; generic/test webhook must remain gated off in production.

## Suggested public endpoints

- `https://www.agri-ci.com` — web application
- `https://api.agri-ci.com` — API

The domain may remain registered at another registrar. DNS is pointed to the DigitalOcean application only when the pilot environment is ready.

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
- `PAYMENT_WEBHOOK_SECRET=<provider-specific production secret>`

Additional provider-specific variables must be added only after a licensed payment provider is selected.

## Required web build variable

- `NEXT_PUBLIC_API_BASE_URL=https://api.agri-ci.com/api/v1`

This value is public by design and is compiled into the Next.js web build.

## Build/run configuration

### API

Source directory: `backend/`

Container: `backend/Dockerfile`

Runtime command is supplied by the image and starts Uvicorn on port 8000.

Health endpoint: `/health`

### Web

Source directory: `web/`

Container: `web/Dockerfile`

Build argument: `NEXT_PUBLIC_API_BASE_URL`

Runtime port: 3000.

## Database migrations

Alembic migrations must be applied against the managed PostgreSQL database before the new API revision receives pilot traffic. Migration failure is a deployment failure; do not continue by manually modifying production tables.

Recommended release command from `backend/`:

```sh
alembic upgrade head
```

## Production gate

Before real transactions, verify that AGRI-CI production readiness reports all required checks as passing, including:

- PostgreSQL production URL
- strong JWT secret
- payment webhook secret
- explicit HTTPS CORS origins (never `*`)
- staging/production environment

A green software gate does not prove external readiness.

## External go-live evidence still required

- DigitalOcean account/resource authorization and billing
- production database and Redis provisioning
- backup/restore validation
- DNS and HTTPS validation
- monitoring/alerts
- licensed payment provider selection and certification
- legal/privacy validation
- named real pilot participants
- controlled field rehearsal

## Deployment sequence

1. Keep preparation changes isolated on `deployment/digitalocean-prep`.
2. Build/test API and web containers in CI.
3. Review the deployment pull request.
4. Only then create/authorize DigitalOcean resources.
5. Provision managed PostgreSQL and Redis.
6. Enter secrets in DigitalOcean, never in GitHub source files.
7. Deploy API and run Alembic migrations.
8. Deploy web with the final API URL as its build variable.
9. Verify health, authentication, CORS, RBAC and transaction smoke tests.
10. Configure DNS/HTTPS.
11. Verify backups and restoration procedure.
12. Integrate/certify the selected licensed payment provider.
13. Execute the controlled field rehearsal before real-money pilot transactions.
