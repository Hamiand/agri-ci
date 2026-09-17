# AGRI-CI — First Pilot Order Control Sheet

Use one copy of this sheet for the first controlled commercial order and for each subsequent order until the pilot coordinator authorizes expansion. The objective is to prove that every physical kilogram and every XOF can be reconciled from farmer allocation to final settlement.

## 1. Order identity

- Release commit SHA: `______________________________`
- Order reference: `______________________________`
- Buyer: `______________________________`
- Product: `______________________________`
- Delivery destination: `______________________________`
- Delivery window: `______________________________`
- Agreed price: `________________ XOF/kg`
- Pilot coordinator: `______________________________`

## 2. Aggregation and farmer allocations

| Farmer / cooperative | Offer ref | Commitment ref | Allocated kg | Accepted? |
|---|---|---|---:|---|
| | | | | |
| | | | | |
| | | | | |
| | | | | |

- Target order quantity: `________________ kg`
- Total accepted allocation: `________________ kg`
- Firm-order gate satisfied: `[ ] YES  [ ] NO`

**Control:** a firm order must not proceed unless the aggregation conditions are satisfied.

## 3. Collection reconciliation

| Farmer | Allocated kg | Actually collected kg | Collection point | Collection ref | Difference kg |
|---|---:|---:|---|---|---:|
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |

- Total allocated: `________________ kg`
- Total collected: `________________ kg`
- Unexplained collection discrepancy: `[ ] NO  [ ] YES`

**Control:** collected quantity must never exceed the farmer's remaining allocation.

## 4. Quality and lots

| Collection ref | Grade | Quality kg | Lot ref | Lot kg | Exception |
|---|---|---:|---|---:|---|
| | | | | | |
| | | | | | |
| | | | | | |

- Total collected quantity: `________________ kg`
- Total graded quantity: `________________ kg`
- Total lot quantity: `________________ kg`
- Nonconforming/rejected quantity: `________________ kg`

**Control:** graded quantity cannot exceed collection quantity and each lot must remain traceable to its quality source.

## 5. Transport and delivery

| Transport ref | Lot(s) | Planned kg | Origin | Destination | Delivered kg | Receiver |
|---|---|---:|---|---|---:|---|
| | | | | | | |
| | | | | | | |

- Total transported capacity: `________________ kg`
- Total delivered: `________________ kg`
- Remaining undelivered: `________________ kg`
- Delivery discrepancy explained: `[ ] YES  [ ] NO`

**Control:** cumulative delivered quantity must never exceed assigned transport capacity.

## 6. Settlement preparation

- Eligible delivered and not-yet-settled quantity: `________________ kg`
- Price: `________________ XOF/kg`
- Gross amount: `________________ XOF`
- Transport deduction: `________________ XOF`
- AGRI-CI service deduction: `________________ XOF`
- Other authorized deduction: `________________ XOF`
- Total deductions: `________________ XOF`
- Expected net farmer amount(s): `________________ XOF`

### Farmer settlement detail

| Farmer | Eligible kg | Gross XOF | Deductions XOF | Net XOF | Payment ref | Provider status |
|---|---:|---:|---:|---:|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |

**Control:** settlement quantity must not exceed delivered quantity. FAILED or REFUNDED payment attempts do not count as settled quantity.

## 7. Provider and ledger reconciliation

- Licensed payment provider: `______________________________`
- Provider transaction/reference: `______________________________`
- Provider final outcome: `______________________________`
- AGRI-CI payment status: `______________________________`
- AGRI-CI ledger net total: `________________ XOF`
- Provider paid/settled total: `________________ XOF`
- Difference: `________________ XOF`
- Difference explained/resolved: `[ ] YES  [ ] NO`

## 8. Incident and dispute record

| Time | Stage | Incident/discrepancy | Evidence/reference | Action | Resolved? |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |

If a critical discrepancy is unresolved, stop new commercial orders until it is understood and reconciled.

## 9. Farmer outcome

For the first order, record the result rather than only the software transaction:

- Quantity farmer expected to sell through AGRI-CI: `________________ kg`
- Quantity actually sold/delivered: `________________ kg`
- Net amount actually received: `________________ XOF`
- Time from delivery to successful payment: `________________`
- Logistics cost per delivered kg: `________________ XOF/kg`
- Farmer reported major difficulty: `______________________________`
- Farmer reported benefit: `______________________________`

## 10. Order close decision

Before closing the order:

- [ ] Allocation reconciled.
- [ ] Collection reconciled.
- [ ] Quality/lots reconciled.
- [ ] Transport/delivery reconciled.
- [ ] Payment/ledger/provider reconciled.
- [ ] Critical incidents resolved.
- [ ] Farmer outcome recorded.

Decision: `[ ] ORDER RECONCILED   [ ] HOLD / INVESTIGATE`

Reviewed by: `______________________________`

Date/time: `______________________________`

## 11. Expansion decision

After the first reconciled order:

- [ ] Repeat same volume before expansion.
- [ ] Increase farmer count.
- [ ] Increase buyer count.
- [ ] Increase maximum volume.
- [ ] Add collection point/transporter.
- [ ] Do not expand yet.

Reason: `____________________________________________________________`

The governing question remains:

> **What actually changed for the farmer?**