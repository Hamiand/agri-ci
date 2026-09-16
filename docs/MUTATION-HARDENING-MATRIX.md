# Quantity/Money Mutation Hardening Matrix — v0.22

| Mutation | RBAC | Object auth | Row lock/integrity | Idempotency |
|---|---|---|---|---|
| Aggregate demand | Buyer | Buyer ownership | quantity locks | YES |
| Commitment accept/decline | Farmer | **Farmer ownership added** | commitment/offer logic | YES |
| Firm order | Buyer | Buyer ownership | exact target gate | YES |
| Collection | Collection/Ops/Admin | allocation validation | quantity validation | YES foundation |
| Quality | Collection/Ops/Admin | collection relationship | QC quantity integrity | YES foundation |
| Lot creation | Transport/Ops/Admin | order/QC relationship | duplicate QC blocked | YES foundation |
| Transport creation/depart | Transport/Ops/Admin | order/lot relationship | lot locks/one assignment | YES foundation |
| Delivery | Ops/Admin | transport relationship | delivery capacity | YES foundation |
| Settlement preparation | Ops/Admin | farmer allocation | unique farmer/order payment | YES foundation |
| Payment success | signed provider webhook | payment ID | payment row lock | provider signature |

## Remaining before gate is green
`YES foundation` means the request is captured by persisted-idempotency infrastructure, but
runtime CI must prove replay returns the completed response for every endpoint. Response
persistence still needs normalization on some legacy router code paths.
