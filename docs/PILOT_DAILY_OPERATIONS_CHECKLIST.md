# AGRI-CI — Pilot Daily Operations Checklist

Use this checklist on every day when the controlled commercial pilot is active. It complements the go-live checklist and incident playbook; it is designed for short daily operational control.

## 1. Start-of-day control

Date: `________________`  Operations lead: `______________________________`

Before accepting new physical or payment activity:

- [ ] AGRI-CI web application is reachable.
- [ ] API health/readiness checks are healthy.
- [ ] Database/critical services show no known outage.
- [ ] No unresolved P1 incident is open.
- [ ] Payment provider has no known blocking outage if payments are expected today.
- [ ] Collection agent(s) expected today are identified.
- [ ] Transporter(s) expected today are identified.
- [ ] Today's collection/delivery orders are known.

If a critical prerequisite is unavailable, do not start the affected real-money or physical step.

## 2. Today's planned activity

| Order ref | Product | Farmer/cooperative | Planned collection kg | Buyer | Planned delivery | Status |
|---|---|---|---:|---|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |

## 3. Collection control

For every collection performed today:

- [ ] Correct order/farmer allocation selected.
- [ ] Actual weight recorded by authorized collection agent.
- [ ] Real collection point recorded.
- [ ] Quantity does not exceed remaining allocation.
- [ ] Any discrepancy is recorded rather than hidden.

Total collected today: `________________ kg`

## 4. Quality and lot control

- [ ] Quality grading references the correct collection.
- [ ] Graded quantity does not exceed collected quantity.
- [ ] Lots are traceable to quality checks.
- [ ] Nonconforming/rejected quantity is recorded when applicable.

Total placed into lots today: `________________ kg`

## 5. Transport and delivery control

- [ ] Transport job uses an authorized transporter account.
- [ ] Origin and destination are real and verified.
- [ ] Assigned lots match the physical shipment.
- [ ] Departure is recorded.
- [ ] Actual delivered quantity is recorded.
- [ ] Delivery receiver is identified.
- [ ] Cumulative delivered quantity does not exceed transported capacity.

Total delivered today: `________________ kg`

## 6. Payment and settlement control

Before preparing any settlement:

- [ ] Delivered eligible quantity has been verified.
- [ ] Already-settled quantity has been considered.
- [ ] Agreed price is verified.
- [ ] Transport deduction is authorized and verified.
- [ ] AGRI-CI service deduction, if any, is authorized and verified.
- [ ] Other deduction, if any, is authorized and verified.
- [ ] Correct licensed payment provider is selected.

After provider processing:

- [ ] Provider reference is retained.
- [ ] Provider outcome and AGRI-CI payment status agree.
- [ ] Failed/refunded attempts are not treated as finally settled.
- [ ] Farmer payment history reflects successful settlement appropriately.

Total successfully settled today: `________________ XOF`

## 7. End-of-day reconciliation

Record totals for the day:

- New demand quantity: `________________ kg`
- New accepted commitment quantity: `________________ kg`
- Collected: `________________ kg`
- Graded/lotted: `________________ kg`
- Delivered: `________________ kg`
- Eligible settlement quantity: `________________ kg`
- Successfully settled quantity: `________________ kg`
- Gross settlement value: `________________ XOF`
- Authorized deductions: `________________ XOF`
- Net farmer payment: `________________ XOF`

Unexplained difference: `[ ] NONE  [ ] YES — incident ref: __________________`

## 8. Incident review

- Open P1 incidents: `________`
- Open P2 incidents: `________`
- Open P3 incidents: `________`

- [ ] Every P1/P2 incident has an owner.
- [ ] Evidence/references have been preserved.
- [ ] No affected order was incorrectly marked reconciled.
- [ ] No pilot expansion is planned while a blocking discrepancy remains unresolved.

## 9. End-of-day decision

- [ ] DAY RECONCILED — normal controlled pilot may continue.
- [ ] HOLD NEW ORDERS — reconciliation/investigation required.
- [ ] HOLD PAYMENTS — payment/provider reconciliation required.
- [ ] STOP PILOT — critical incident or infrastructure problem.

Reason/notes: `____________________________________________________________`

Operations lead: `______________________________`

Pilot coordinator: `______________________________`

Time closed: `______________________________`

## 10. Daily public-value observation

Record one short observation from the field, not just software metrics:

**What changed for the farmer today?**

`__________________________________________________________________________`

This daily observation should later feed the pilot review alongside quantities, costs, payment delay and disputes.