# AGRI-CI — External Go-Live Blockers

**Purpose:** keep external launch dependencies separate from software completion. A box may be checked only after real evidence exists.

## 1. Licensed payment provider

- [ ] Provider selected.
- [ ] Commercial/legal relationship established as required.
- [ ] Production credentials issued.
- [ ] Provider-specific webhook authentication implemented and verified.
- [ ] Replay protection verified with provider-specific mechanism.
- [ ] Sandbox/certification acceptance completed where required.
- [ ] Settlement and reconciliation procedure tested.
- [ ] Operational escalation contact identified.

**Current verified status:** not completed in repository evidence.

## 2. Production infrastructure

- [ ] Production hosting selected/provisioned.
- [ ] Public HTTPS endpoint verified.
- [ ] Production secrets managed outside repository/default values.
- [ ] Production PostgreSQL provisioned.
- [ ] Required Redis/storage provisioned.
- [ ] Backups running.
- [ ] Real restore drill completed and documented.
- [ ] Monitoring/alerting operational.
- [ ] Operational logs retained appropriately.

**Current verified status:** not completed in repository evidence.

## 3. Real pilot partners

- [ ] Pilot product selected.
- [ ] Pilot production area selected.
- [ ] Farmer(s) or cooperative formally identified/onboarded.
- [ ] Buyer(s) formally identified/onboarded.
- [ ] Collection point confirmed.
- [ ] Transporter and responsible operational contacts confirmed.
- [ ] Authorized AGRI-CI pilot operators confirmed.

**Current verified status:** not completed in repository evidence.

## 4. Controlled field procedure

- [ ] Named pilot coordinator.
- [ ] Named operations manager.
- [ ] Named collection agent(s).
- [ ] Technical incident contact.
- [ ] Commercial/dispute escalation contact.
- [ ] Initial controlled volume agreed.
- [ ] Quality rules agreed with participants.
- [ ] Price and authorized deductions agreed.
- [ ] Stop/rollback criteria accepted by operating team.
- [ ] First-order reconciliation responsibility assigned.

**Current verified status:** framework documented; real named actors/agreements not verified.

## 5. Legal and privacy

- [ ] Pilot terms reviewed for applicable jurisdiction.
- [ ] Privacy/data handling reviewed.
- [ ] Payment/commercial compliance reviewed.
- [ ] Required participant notices/consents approved.

**Current verified status:** not completed in repository evidence.

---

## Release rule

The AGRI-CI software technical gate and these external go-live blockers are intentionally independent.

Do not mark this document complete because CI is green. Do not mark CI incomplete merely because an external partner has not yet been selected.

Real-money field activation requires the applicable external blockers above to be verified.