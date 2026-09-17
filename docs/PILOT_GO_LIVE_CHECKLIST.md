# AGRI-CI — Pilot Go-Live Checklist

Use this checklist immediately before activating the first controlled commercial pilot. Every blocking item must be explicitly confirmed. An unchecked blocking item means **NO-GO** for real-money activation.

## A. Release candidate

- [ ] Exact deployed commit SHA recorded: `______________________________`
- [ ] AGRI-CI Pilot CI green on that exact SHA.
- [ ] Web build green.
- [ ] Backend/PostgreSQL integration and concurrency tests green.
- [ ] AGRI-CI-001 authenticated HTTP/PostgreSQL E2E green.
- [ ] RC1 runtime/commercial gate green.
- [ ] No unresolved critical defect in farmer → buyer → operations → settlement path.

## B. Production environment — BLOCKING

- [ ] Public API is served through HTTPS.
- [ ] Production domain/API URL recorded: `______________________________`
- [ ] Database is production PostgreSQL, not SQLite/local development storage.
- [ ] Redis is available for the production environment where required.
- [ ] JWT secret is strong, production-only and not committed to Git.
- [ ] Payment webhook secret/credentials are production-only and not committed to Git.
- [ ] CORS allows only approved HTTPS pilot origins.
- [ ] Production environment passes AGRI-CI preflight/readiness checks.
- [ ] Production database backup has succeeded.
- [ ] A restore from backup has been tested and documented.
- [ ] Technical monitoring/alerting contacts are identified.

## C. Payment provider — BLOCKING FOR REAL MONEY

- [ ] Licensed/authorized payment provider selected: `______________________________`
- [ ] Provider commercial/technical agreement confirmed for pilot use.
- [ ] Production credentials issued and stored securely.
- [ ] Provider-specific webhook authentication implemented and verified.
- [ ] Duplicate/replayed provider events tested safely.
- [ ] SUCCESS, FAILED and REFUNDED provider outcomes tested.
- [ ] Provider transaction reference is retained in AGRI-CI.
- [ ] Settlement reconciliation procedure agreed with responsible operator.
- [ ] Named provider escalation contact recorded: `______________________________`

If this section is incomplete, AGRI-CI may be demonstrated with test transactions only; real-money processing must remain disabled.

## D. Pilot actors — BLOCKING

- [ ] Pilot coordinator identified: `______________________________`
- [ ] Operations manager identified: `______________________________`
- [ ] Collection agent(s) identified and authorized.
- [ ] Farmer/cooperative participants identified and onboarded.
- [ ] Buyer(s) identified and onboarded.
- [ ] Transporter account(s) identified and authorized.
- [ ] Collection point(s) confirmed.
- [ ] Delivery destination(s) confirmed.
- [ ] Commercial/dispute escalation contact identified.

## E. First product and commercial conditions — BLOCKING

- [ ] Pilot product: `______________________________`
- [ ] Production area: `______________________________`
- [ ] Initial maximum pilot quantity: `________________ kg`
- [ ] Delivery window agreed.
- [ ] Quality grading rules agreed and understood.
- [ ] Price formation/agreed price documented.
- [ ] Transport cost rule documented.
- [ ] AGRI-CI service cost, if any, documented and authorized.
- [ ] Other permitted deductions, if any, documented before settlement.
- [ ] Farmer net-payment explanation understood by responsible operators.

## F. Legal/privacy/operational approval — BLOCKING

- [ ] Pilot terms/participant agreement reviewed for the operating jurisdiction.
- [ ] Privacy/data-handling notice reviewed.
- [ ] Personal data collected is limited to what the pilot actually needs.
- [ ] Payment/commercial responsibilities are documented.
- [ ] Dispute and incident escalation procedure is documented.
- [ ] Authorized person has approved controlled pilot activation.

## G. Dry run before real transaction

Perform one end-to-end dry run with test/non-cash data:

- [ ] Farmer login and future harvest declaration.
- [ ] Offer creation.
- [ ] Buyer demand creation.
- [ ] Matching/aggregation.
- [ ] Commitment accept/decline and replacement if required.
- [ ] Firm order creation.
- [ ] Collection with actual test weight and collection point.
- [ ] Quality grading and lot creation.
- [ ] Transport assignment and departure.
- [ ] Partial/full delivery confirmation.
- [ ] Settlement preparation on delivered quantity only.
- [ ] Payment-provider test event.
- [ ] Farmer payment-history visibility.
- [ ] Final quantity and ledger reconciliation.

## H. GO / NO-GO decision

### Mandatory NO-GO conditions

Do not activate real-money pilot operation if any of the following remains true:

- Production HTTPS/secrets/database/backup controls are incomplete.
- Licensed payment-provider production integration is not verified.
- A critical quantity, authorization, payment or ledger defect is unresolved.
- Pilot actors or responsibilities are not identified.
- Commercial deductions are not agreed/documented.
- Required legal/privacy approval is incomplete.

### Decision record

- Decision: `[ ] GO   [ ] NO-GO`
- Date/time: `______________________________`
- Release SHA: `______________________________`
- Approved by: `______________________________`
- Pilot maximum quantity: `________________ kg`
- Notes: `____________________________________________________________`

## I. First-day control

For the first real order, the pilot coordinator must confirm before increasing volume:

- [ ] Ordered quantity reconciles with accepted farmer allocations.
- [ ] Collected quantity reconciles with allocation.
- [ ] Quality and lot quantities reconcile with collection.
- [ ] Transport and delivery quantities reconcile with lots.
- [ ] Settled quantity does not exceed delivered quantity.
- [ ] Gross, deductions and farmer net payment reconcile exactly.
- [ ] Provider reference and AGRI-CI payment status agree.
- [ ] No unresolved critical incident exists.

Only then may the controlled pilot proceed to another order or a larger volume.
