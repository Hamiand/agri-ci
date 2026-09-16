# AGRI-CI-001 — Database/HTTP Acceptance Scenario

1. Create Koffi 400 kg, Awa 750 kg, Mariam 600 kg, Yao 300 kg, Cooperative A 1,400 kg.
2. Buyer publishes 3,000 kg tomato demand, Abidjan, 16–18 May 2027, quality A/B, target 760 XOF/kg.
3. Run matching.
4. Aggregate exactly: 400 + 750 + 600 + 300 + 950 = 3,000 kg.
5. Koffi/Awa/Mariam/Coop A accept; Yao declines.
6. Accepted/proposed state drops to 2,700 kg.
7. Automatic refill may reuse Cooperative A's remaining 450 kg and proposes 300 kg.
8. Cooperative A accepts the second 300 kg.
9. Gate reaches 3,000/3,000 and firm order is created once.
10. Concurrent duplicate order creation with same idempotency key returns one logical order.
11. Collection records physical weights; Farmer 0047 reference: 350 announced → 327 received.
12. Quality A 220 + B 91 + C 16 = 327.
13. Quality chunks become lots exactly once.
14. Lots enter one transport only.
15. Delivery closes physical chain.
16. Settlement uses collected quantity and writes auditable gross/deduction/net ledger entries.
17. Licensed provider integration is external; development provider-success endpoint is not production acceptance.
