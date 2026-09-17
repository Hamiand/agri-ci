# AGRI-CI — Commercial Pilot Release 1.0 Gate

This document freezes the scope of the first controlled commercial pilot. It is a release gate, not a claim that unrestricted production launch is already authorized.

## 1. Pilot objective

Prove one complete, traceable agricultural transaction flow with real pilot actors and controlled volumes:

**Farmer → future harvest → offer → buyer demand → matching/aggregation → commitment → confirmed order → collection → quality/lot → transport → delivery → settlement preparation → licensed payment provider.**

The existing AGRI-CI-001 automated scenario remains the reference technical proof for the core transaction chain.

## 2. Included in Release 1.0

### Farmer
- Authentication and role-based workspace.
- Declare a future harvest.
- Create an offer from a declared harvest.
- See active buyer demand.
- Accept or decline AGRI-CI commitments.
- Follow collection allocations as read-only information.
- View real payment history.

### Buyer
- Authentication and role-based workspace.
- Publish demand.
- View and resume aggregation.
- Create a firm order only after the aggregation gate is satisfied.
- Track collection, quality, transport and delivery.

### Operations
- Record real collection quantity and collection point.
- Record quality and create lots.
- Plan and start transport with an authorized transporter.
- Confirm partial or complete delivery.
- Prepare settlement only for delivered and not-yet-settled quantity.

### Core controls
- PostgreSQL transactional integrity and Alembic migrations.
- Object/role authorization on sensitive operations.
- Idempotency on sensitive mutations.
- Quantity locking and concurrency protection.
- Canonical API error envelopes and request IDs.
- Audit/domain events and retry-safe transactional outbox.
- Incremental delivery and incremental settlement.
- Failed/refunded settlement replacement semantics.
- Payment ledger accounting proof.
- Production-readiness configuration checks.
- CI proof for backend, PostgreSQL integration/E2E and pilot web build.

## 3. Explicitly outside Release 1.0

These functions are valuable but are not blockers for the first controlled commercial pilot:

- AI/ML forecasting.
- National AGRI-CI Radar.
- Livestream commerce.
- USSD/SMS/voice channels.
- Native Flutter application.
- Nationwide multi-region scaling.
- Advanced geospatial logistics optimization.
- Automated farmer reliability scoring.

They must not delay the controlled pilot.

## 4. External go-live blockers

The software gate alone does **not** authorize handling unrestricted real commercial transactions. Before real-money field operation, AGRI-CI still requires:

1. **Licensed payment provider** — production credentials, provider-specific webhook authentication/replay protection, certification/sandbox acceptance and settlement reconciliation procedure.
2. **Production infrastructure** — HTTPS endpoint, managed secrets, production PostgreSQL/Redis/storage, backups with a real restore drill, monitoring/alerting and operational logs.
3. **Pilot operating partners** — identified farmers/cooperative, buyer(s), collection point, transporter and authorized AGRI-CI operators.
4. **Controlled field procedure** — small initial volume, named responsibilities, incident/dispute escalation, reconciliation and rollback/stop criteria.
5. **Legal/privacy approval** — terms, privacy/data handling and local operational/payment compliance reviewed for the pilot jurisdiction.

## 5. Technical release gate

A candidate is technically acceptable for **Commercial Pilot Release 1.0** only when all of the following are true on the same `main` revision:

- Pilot web build succeeds.
- Backend compile/import and non-integration tests succeed.
- Alembic upgrade against PostgreSQL succeeds.
- PostgreSQL integration/concurrency tests succeed.
- AGRI-CI-001 authenticated HTTP/PostgreSQL end-to-end proof succeeds.
- RC1 runtime/commercial configuration gate succeeds.
- No unresolved blocker remains in the essential farmer, buyer or operations transaction path.

## 6. Field-pilot acceptance indicators

During the controlled field pilot, record at minimum:

- Quantity announced, offered, committed, collected, delivered and settled.
- Percentage sold before harvest.
- Collection-to-delivery time.
- Logistics cost per kg.
- Payment delay.
- Number of disputes and their resolution time.
- Net amount received by each farmer.
- Any quantity, quality, identity or payment discrepancy.

The central question remains:

> **What actually changed for the farmer?**

## 7. Release decision

**Current meaning of “Release 1.0 ready”:** the AGRI-CI software core and pilot web interface have passed the technical gate and are ready to be connected to the controlled production environment and real pilot partners.

**It does not mean:** nationwide launch, unrestricted public onboarding, or unverified real-money processing.
