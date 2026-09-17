# AGRI-CI — DigitalOcean Activation Checklist

[Version française](DIGITALOCEAN_ACTIVATION_CHECKLIST_FR.md)

This checklist begins only when the project owner decides to authorize the creation of DigitalOcean resources. It contains no secrets.

## Before clicking “Create Resources”

- [ ] The exact Git revision to deploy has been identified.
- [ ] GitHub Actions is green for that revision, including the production Docker images.
- [ ] The cost displayed by DigitalOcean has been reviewed and accepted by the project owner.
- [ ] Managed PostgreSQL is planned as the production database.
- [ ] A compatible Redis/Valkey service is planned if required by the runtime.
- [ ] The API, Web application, transactional worker, and Alembic PRE_DEPLOY job are configured.
- [ ] No real password, token, or secret is stored in GitHub.

## API / worker environment variables

Configure the following as runtime environment variables in DigitalOcean:

- `APP_ENV=production`
- `APP_DEBUG=false`
- `DATABASE_URL` = managed PostgreSQL connection (prefer a private connection when available)
- `REDIS_URL` = Redis/Valkey connection
- `JWT_SECRET` = strong random secret, stored as an encrypted secret
- `JWT_ALGORITHM=HS256`
- `JWT_ACCESS_TOKEN_MINUTES=30`
- `JWT_REFRESH_TOKEN_DAYS=30`
- `CORS_ORIGINS=https://www.agri-ci.com`
- `PAYMENT_WEBHOOK_SECRET` = only the production value corresponding to the selected payment provider

The worker uses the same PostgreSQL configuration as the API. It has no public HTTP route.

## Web variable

When building the Web application:

- `NEXT_PUBLIC_API_BASE_URL=https://api.agri-ci.com`

This value is not a secret.

## Migration

Create a `PRE_DEPLOY` job:

```sh
alembic upgrade head
```

The job must use the same PostgreSQL database as the API. If the migration fails, the deployment must be considered failed.

## Checks after the first deployment

- [ ] `/health` returns HTTP 200.
- [ ] `/ready` confirms access to PostgreSQL.
- [ ] `/commercial-readiness` passes with the intended production configuration.
- [ ] The Web application loads correctly and calls the API over HTTPS.
- [ ] CORS allows only the intended origins and never `*` in production.
- [ ] The generic/test payment webhook remains blocked in production.
- [ ] The worker starts without public exposure.
- [ ] Logs do not expose any secrets.

## Domain and HTTPS

Do not change DNS until the temporary DigitalOcean URLs have been validated.

Planned targets:

- `www.agri-ci.com` → AGRI-CI Web
- `api.agri-ci.com` → AGRI-CI API

Then verify the TLS/HTTPS certificate before any pilot traffic is allowed.

## Data protection and recovery

Before any real commercial transaction:

- [ ] automatic PostgreSQL backups are confirmed;
- [ ] backup retention is documented;
- [ ] restoration has actually been tested;
- [ ] the incident procedure is documented;
- [ ] pilot owners/responsible persons are identified.

## Payments and field operations

Technical deployment does not remove the following external blockers:

- licensed payment provider selected and certified;
- legal/privacy validation;
- real farmers/cooperative and buyer;
- collection point and transporter;
- controlled field rehearsal;
- first low-volume transaction and final reconciliation.

## User intervention point

Repository preparation can be completed without spending money. The project owner's first mandatory intervention occurs when the DigitalOcean account must be authorized, the displayed cost must be confirmed, and paid resources must be created. No purchase should be made automatically.
