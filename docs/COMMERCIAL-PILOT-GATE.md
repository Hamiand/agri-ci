# AGRI-CI Commercial Pilot Release Gate

No real-money commercial pilot is approved until every BLOCKER below is green.

## BLOCKERS
- [ ] PostgreSQL `alembic upgrade head` passes in staging
- [ ] FastAPI application imports and starts in staging
- [ ] Full AGRI-CI-001 public HTTP transaction passes
- [ ] 400 kg two-session PostgreSQL concurrency race passes
- [ ] endpoint/object authorization matrix passes in runtime CI (code rollout substantially complete)
- [ ] persisted idempotency replay behavior passes runtime CI on every money/quantity-changing endpoint
- [ ] licensed payment provider sandbox is connected
- [ ] signed webhook verification passes selected provider certification (generic HMAC seam built)
- [ ] HTTPS/TLS enabled
- [ ] production secrets are externalized and rotated
- [ ] database automated backups enabled
- [ ] restore test completed
- [ ] error monitoring and operational alerts enabled
- [ ] legal Terms of Service / Privacy Notice approved for Côte d'Ivoire operations
- [ ] farmer/buyer consent and dispute procedure approved
- [ ] named collection agents and transport partners trained
- [ ] pilot support/escalation owner assigned

## Pilot scope after gate
- 20–50 farmers
- one product
- one production area
- 2–5 verified buyers
- one destination market
- 1–2 transport partners
- limited transaction ceiling
- daily operational review

## Pilot success metrics
sale rate, post-harvest loss, net farmer XOF/kg, payment delay, logistics XOF/kg,
delivery success, disputes/100 orders, repeat buyers, farmer satisfaction.
