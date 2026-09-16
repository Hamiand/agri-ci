# AGRI-CI Production Infrastructure Gate

## Application
- HTTPS enforced at ingress/reverse proxy.
- Secrets supplied by secret manager/environment, never committed.
- CORS restricted to AGRI-CI origins.
- Security/request-ID middleware enabled.
- Staging and production use separate databases and credentials.

## PostgreSQL
- managed/HA PostgreSQL preferred for commercial deployment.
- encrypted storage and encrypted connections.
- automated daily backups + point-in-time recovery where provider supports it.
- monthly restore drill during pilot.
- migration applied before application rollout.

## Monitoring
- uptime check `/health`.
- dependency readiness `/ready`.
- production configuration `/production-readiness` restricted at ingress if desired.
- alert on 5xx rate, DB saturation, payment failures, queue backlog and disk/storage problems.
- never log passwords, JWTs, payment secrets or sensitive evidence.

## Recovery targets for pilot
Initial operational targets, to be validated with hosting provider:
- restore service within 4 hours after major infrastructure failure;
- lose no more than 24 hours of data from backup alone; use PITR to improve this materially.

These are pilot targets, not claims of current SLA.
