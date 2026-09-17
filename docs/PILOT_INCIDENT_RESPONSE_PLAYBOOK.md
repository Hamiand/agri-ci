# AGRI-CI — Pilot Incident Response Playbook

This playbook defines what the pilot team must do when something goes wrong during the first controlled commercial operations. Its purpose is to protect traceability, farmer/buyer interests and payment integrity while keeping the response simple enough for field use.

## 1. Core rule

When a serious discrepancy is detected:

1. **Stop the affected transaction step.**
2. **Preserve the existing AGRI-CI records and evidence.**
3. **Do not overwrite history to make quantities or money appear to reconcile.**
4. **Identify the responsible operational owner.**
5. **Reconcile before resuming or expanding the pilot.**

A problem in one order does not require deleting or rewriting unrelated valid orders.

## 2. Severity levels

### P1 — Critical

Examples:
- Same physical quantity appears allocated or settled twice.
- Unauthorized user can access or mutate another actor's protected transaction.
- Settled quantity exceeds delivered quantity.
- AGRI-CI says payment succeeded but the licensed provider cannot verify it, or vice versa.
- Ledger/provider amounts cannot be reconciled.
- Production database integrity or recovery capability is compromised.

**Action:** immediately pause new real-money orders. Escalate to pilot coordinator, technical owner and payment/operations owner as applicable. Resume only after cause, correction and reconciliation are documented.

### P2 — Major

Examples:
- Collection, quality, lot, transport or delivery quantity discrepancy that cannot be explained immediately.
- Payment is delayed or failed but no double settlement occurred.
- Transport/delivery evidence is incomplete.
- One essential pilot screen/API is unavailable while data remains safe.

**Action:** hold the affected order/step. Do not increase pilot volume. Investigate and reconcile before closing that order.

### P3 — Minor

Examples:
- Non-critical display problem.
- Temporary retryable network error.
- Typographical/non-financial operational note requiring clarification.

**Action:** record the issue, use approved retry/recovery procedure and continue only if quantities, authorization and money remain unambiguous.

## 3. Incident record

For every P1/P2 incident record:

- Incident reference: `______________________________`
- Date/time detected: `______________________________`
- Detected by: `______________________________`
- Order/payment/collection/transport reference: `______________________________`
- Severity: `[ ] P1  [ ] P2  [ ] P3`
- Stage affected: `______________________________`
- What was observed: `__________________________________________________________`
- Expected state: `____________________________________________________________`
- Evidence retained: `___________________________________________________________`
- Immediate action taken: `______________________________________________________`
- Operational owner: `______________________________`
- Technical owner if needed: `______________________________`
- Payment-provider contact if needed: `______________________________`

## 4. Quantity discrepancy procedure

If quantities do not reconcile:

1. Freeze progression of the affected order step.
2. Compare accepted allocation → collection → quality → lot → transport → delivery → settled quantity.
3. Identify the first stage where the difference appears.
4. Compare AGRI-CI references with field evidence (weight record, lot reference, delivery confirmation, timestamped evidence where available).
5. Correct only through the approved business action; never fabricate a later quantity merely to balance totals.
6. Re-run the order reconciliation sheet.

**Mandatory control:** settlement must never be used to compensate for an unresolved physical-quantity discrepancy.

## 5. Payment incident procedure

### Provider reports FAILED

- Keep the failed attempt as historical evidence.
- Confirm AGRI-CI does not count the failed quantity as settled.
- Verify the provider reference/status.
- Retry only through the approved replacement settlement flow.
- Reconcile the successful replacement separately.

### Provider reports REFUNDED

- Preserve the refunded payment record.
- Confirm refunded quantity is not treated as finally settled.
- Determine why refund occurred before replacement payment.
- Reconcile provider and AGRI-CI records before retry.

### AGRI-CI and provider disagree

Treat as **P1** until reconciled. Do not create manual success merely to close the order. Compare provider reference, amount, status, webhook/event evidence and AGRI-CI ledger/payment state.

## 6. Authorization/security incident

If an actor appears able to see or change an object outside their authorized role or ownership:

- Stop use of the affected function for real transactions.
- Record account, role, object/reference and action attempted.
- Preserve request/trace information where available.
- Do not ask field users to work around authorization by sharing accounts.
- Technical owner must verify the correction and regression tests before resuming that function.

A confirmed cross-account authorization failure is **P1**.

## 7. Service outage / connectivity

If the application is temporarily unavailable:

- Do not repeatedly create the same commercial action with new identifiers unless the previous result is known.
- Preserve any field evidence collected during the outage.
- When service returns, verify whether the original action was committed before retrying.
- Use AGRI-CI idempotent/retry behavior where provided.
- Reconcile affected order state before moving to the next physical step.

## 8. Backup/database incident

If production database backup/recovery capability is unavailable or database integrity is uncertain:

- Pause new real-money transactions.
- Preserve infrastructure/application logs.
- Confirm database state and latest usable backup.
- Restore to an isolated environment if recovery verification is required.
- Resume only after the technical owner confirms integrity and recovery capability.

## 9. Evidence preservation

Do not delete or overwrite evidence associated with a serious incident. Retain, as applicable:

- AGRI-CI business references.
- Request/trace identifiers.
- Collection/quality/lot records.
- Transport/delivery references.
- Payment and provider references.
- Ledger entries.
- Relevant timestamps.
- Field documents/photos already legitimately collected for the pilot.
- Incident decisions and reconciliation notes.

## 10. Resume decision

For a P1/P2 incident, record:

- Root cause understood: `[ ] YES  [ ] NO`
- Affected quantities reconciled: `[ ] YES  [ ] NO  [ ] N/A`
- Payment/provider reconciled: `[ ] YES  [ ] NO  [ ] N/A`
- Technical correction verified: `[ ] YES  [ ] NO  [ ] N/A`
- Regression test/proof completed when software changed: `[ ] YES  [ ] NO  [ ] N/A`
- Operational procedure updated if needed: `[ ] YES  [ ] NO  [ ] N/A`
- Incident closed by: `______________________________`
- Date/time: `______________________________`

Decision: `[ ] RESUME AFFECTED FLOW   [ ] KEEP ON HOLD`

## 11. Expansion rule after an incident

Do not increase pilot volume immediately after a P1 incident. First complete and reconcile at least one controlled order through the corrected flow. Expansion remains a deliberate decision based on evidence, not on the desire to recover lost time.