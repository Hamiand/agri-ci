# AGRI-CI — Pilot Roles and Responsibilities

This document assigns operational ownership for the first controlled commercial pilot. One person may hold more than one role in a very small pilot, but every responsibility below must have a named owner before GO-LIVE.

## 1. Pilot coordinator

**Owns:** overall GO/NO-GO, pilot scope and stop/resume decisions.

Responsibilities:
- Confirm go-live checklist is complete.
- Approve initial product, area, participants and maximum volume.
- Ensure blocking incidents stop expansion.
- Confirm end-of-order and end-of-day reconciliation.
- Decide whether pilot volume may expand.

Named owner: `______________________________`

## 2. Operations manager

**Owns:** daily physical transaction flow.

Responsibilities:
- Coordinate collection, quality, lots, transport and delivery.
- Ensure authorized users perform operational actions.
- Verify real locations, quantities and responsible actors.
- Review daily operations checklist.
- Escalate unexplained discrepancies immediately.

Named owner: `______________________________`

## 3. Collection agent

**Owns:** reliable recording of produce physically received.

Responsibilities:
- Select correct farmer/order allocation.
- Record actual received weight.
- Record real collection point.
- Never exceed remaining allocated quantity.
- Report discrepancies instead of altering history to hide them.

Named owner(s): `______________________________`

## 4. Quality / lot operator

**Owns:** grading and traceable lot creation.

Responsibilities:
- Apply the agreed grading rules.
- Ensure graded quantity does not exceed collection quantity.
- Create lots traceable to source quality checks.
- Record nonconforming/rejected quantity according to pilot procedure.

Named owner: `______________________________`

## 5. Transport coordinator

**Owns:** shipment assignment and physical movement traceability.

Responsibilities:
- Use authorized transporter accounts only.
- Confirm origin, destination, vehicle/driver where applicable.
- Ensure assigned AGRI-CI lots match the physical shipment.
- Record departure and escalate transport incidents.

Named owner: `______________________________`

## 6. Delivery operator

**Owns:** final delivered quantity confirmation.

Responsibilities:
- Confirm actual delivered quantity.
- Record the identified receiver.
- Never record cumulative delivery above transport capacity.
- Escalate quantity/quality disagreement before settlement.

Named owner: `______________________________`

## 7. Settlement operator

**Owns:** correct preparation of farmer settlement.

Responsibilities:
- Settle only delivered, not-yet-settled eligible quantity.
- Verify agreed price.
- Enter only documented and authorized deductions.
- Use the approved licensed payment provider.
- Preserve provider references and outcomes.
- Never mark a provider payment successful merely to close an order.

Named owner: `______________________________`

## 8. Payment reconciliation owner

**Owns:** AGRI-CI ↔ payment-provider reconciliation.

Responsibilities:
- Compare provider reference, amount and final status with AGRI-CI payment/ledger records.
- Confirm FAILED/REFUNDED attempts are not treated as final settlement.
- Escalate any AGRI-CI/provider disagreement as critical until reconciled.
- Approve payment reconciliation before order closure.

Named owner: `______________________________`

## 9. Technical owner

**Owns:** application/infrastructure availability and technical incident response.

Responsibilities:
- Maintain production deployment and readiness.
- Protect production secrets and configuration.
- Verify backup/recovery and monitoring.
- Investigate application, authorization, database and webhook incidents.
- Require regression proof before resuming a flow after a software correction.

Named owner: `______________________________`

## 10. Farmer / cooperative focal point

**Owns:** participant communication with producers.

Responsibilities:
- Ensure farmers understand harvest estimate vs quantity offered.
- Explain commitments, collection, quality and settlement process.
- Communicate collection arrangements.
- Capture farmer questions/disputes and route them to the correct owner.
- Record practical farmer feedback during pilot review.

Named owner: `______________________________`

## 11. Buyer focal point

**Owns:** buyer communication and commercial fulfillment coordination.

Responsibilities:
- Confirm demand quantity, quality, delivery window and destination.
- Explain aggregation vs firm order.
- Coordinate delivery confirmation and buyer-side discrepancy escalation.

Named owner: `______________________________`

## 12. Incident escalation chain

1. Physical quantity/quality issue → Operations manager.
2. Transport/delivery issue → Transport coordinator + Operations manager.
3. Payment issue → Settlement operator + Payment reconciliation owner.
4. Application/security/database issue → Technical owner.
5. Unresolved major/critical issue → Pilot coordinator.

No participant should solve a control problem by sharing accounts, bypassing authorization, inventing quantities or manually changing payment outcomes.

## 13. Separation of duties for the controlled pilot

Where staffing permits, the person preparing a settlement should not be the only person reconciling that same payment. At minimum, the pilot coordinator or payment reconciliation owner should independently review the first real orders.

For critical corrections, preserve an evidence trail showing who detected, investigated, corrected and approved resumption.

## 14. Pre-GO ownership check

Before real-money activation:

- [ ] Every role required for the chosen pilot scope has a named owner.
- [ ] Every owner understands their stop/escalation responsibility.
- [ ] No critical step depends on an unidentified person.
- [ ] Payment reconciliation has an independent reviewer where practical.
- [ ] Pilot coordinator has final GO/NO-GO authority.

Decision: `[ ] OWNERSHIP COMPLETE   [ ] NOT READY`

Date: `______________________________`

Approved by: `______________________________`