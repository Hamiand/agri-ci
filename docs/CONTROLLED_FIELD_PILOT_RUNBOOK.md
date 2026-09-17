# AGRI-CI — Controlled Field Pilot Runbook

This runbook turns Commercial Pilot Release 1.0 into a small, controlled field operation. It deliberately avoids nationwide launch conditions.

## 1. Pilot principle

Start with one agricultural product, one clearly bounded production area, a small group of identified farmers, identified buyer(s), one collection workflow, authorized transport and a licensed payment provider.

The first field objective is not maximum transaction volume. It is to prove that AGRI-CI can complete one real transaction chain accurately, traceably and safely.

## 2. Minimum actors before opening the pilot

The pilot coordinator must identify and record:

- AGRI-CI pilot coordinator.
- Authorized operations manager.
- Collection agent(s).
- Farmer or cooperative participants.
- Buyer(s).
- Transporter account(s) and responsible driver/vehicle information.
- Collection point(s).
- Licensed payment provider and operational contact.
- Technical incident contact.
- Commercial/dispute escalation contact.

No anonymous operational actor should record collection, transport, delivery or settlement activity.

## 3. Before the first transaction

### Technical checks

- Deploy the exact release candidate that passed the AGRI-CI CI gate.
- Confirm HTTPS is active for public endpoints.
- Confirm production secrets are not repository/default values.
- Confirm PostgreSQL backup succeeds.
- Perform and document at least one restore drill before real-money operation.
- Confirm monitoring/alerts for API failure, database availability and payment webhook failure.
- Confirm `/health`, `/ready`, production-readiness and commercial-readiness checks are healthy.
- Confirm the production payment webhook uses the selected provider's verified authentication mechanism.

### Operational checks

- Verify farmer, buyer, transporter and operator identities/accounts.
- Confirm product, expected quantities and delivery window.
- Confirm actual collection location.
- Confirm quality grading rules understood by farmer, buyer and collection team.
- Confirm commercial price and every authorized deduction before settlement preparation.
- Confirm transport responsibility, origin and destination.
- Confirm dispute escalation contacts.

## 4. First transaction sequence

1. Farmer declares future harvest.
2. Farmer creates an offer for no more than available harvest quantity.
3. Buyer publishes real demand.
4. AGRI-CI performs matching and aggregation.
5. Farmers accept or decline commitments.
6. AGRI-CI creates the firm order only after the aggregation gate is satisfied.
7. Authorized collection agent records actual received weight and real collection point.
8. Authorized operator records quality and creates traceable lots.
9. Authorized operator assigns lots to an identified transporter.
10. Transport departure is recorded.
11. Authorized operator records actual delivered quantity and receiver.
12. AGRI-CI prepares settlement only for delivered, not-yet-settled quantity.
13. Licensed payment provider processes the payment.
14. AGRI-CI records provider outcome and ledger entries.
15. Operations reconcile order, quantities, provider reference and farmer net payment.

## 5. Mandatory reconciliation after each pilot order

For every order, compare:

| Control | Expected result |
|---|---|
| Ordered quantity | Traceable to accepted aggregation allocations |
| Collected quantity | Never exceeds allocated farmer quantity |
| Quality quantity | Never exceeds collected quantity |
| Lot quantity | Traceable to quality checks |
| Transported quantity | Traceable to assigned lots |
| Delivered quantity | Never exceeds transport capacity |
| Settled quantity | Never exceeds delivered quantity |
| Failed/refunded payment | Does not count as settled quantity |
| Gross amount | Delivered settlement quantity × agreed price |
| Deductions | Only actually authorized costs |
| Net farmer amount | Gross minus authorized deductions |
| Provider reference | Unique/consistent with provider outcome |

Any unexplained mismatch stops progression to a larger pilot volume.

## 6. Stop criteria

Pause new commercial transactions if any of the following occurs:

- Quantity is allocated or settled twice.
- A user accesses an object outside their authorized role/ownership.
- Collected, delivered or settled quantity cannot be reconciled.
- Payment provider outcome cannot be verified.
- Ledger and provider settlement disagree.
- Production database backup is unavailable.
- Critical API/database/payment monitoring is unavailable for an extended pilot period.
- A serious dispute cannot be traced to recorded evidence.

Existing records must be preserved for investigation; do not hide or overwrite discrepancies.

## 7. Expansion rule

Increase pilot volume or participant count only after completed orders have been reconciled without unresolved critical discrepancies.

Expand one dimension at a time where practical: more farmers, more buyers, more volume, another collection point, another transporter, then additional products/regions.

Do not treat a successful small pilot as proof of nationwide operational capacity.

## 8. Pilot evidence to retain

For each order retain:

- Demand and aggregation references.
- Farmer commitments and allocations.
- Collection weights and locations.
- Quality checks and lot references.
- Transport and delivery references.
- Settlement/payment references.
- Ledger totals and deductions.
- Provider reconciliation result.
- Disputes/incidents and resolution.
- Timing of major steps.

## 9. Pilot success review

At the end of the first controlled cycle, answer:

- How much was announced, offered, committed, collected, delivered and paid?
- How much was sold before harvest?
- What was the farmer's net price and net payment?
- What was the logistics cost per kg?
- How long did payment take after delivery?
- Were there disputes, quantity discrepancies or payment retries?
- Did the buyer receive the expected quantity and quality?
- Which operational step caused the most delay or manual work?

The final public-value question remains:

> **What actually changed for the farmer?**

## 10. Current release boundary

Passing this runbook's software checks means AGRI-CI is ready for a controlled pilot deployment. Real-money activation still depends on the selected licensed payment provider, production infrastructure, pilot partners and applicable legal/privacy approval.