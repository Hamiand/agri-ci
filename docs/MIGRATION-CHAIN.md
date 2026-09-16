# Alembic Migration Chain (static inspection)

- `0001_foundation.py`: revision `0001_foundation`, down `None`
- `0002_farmer_market.py`: revision `0002_farmer_market`, down `0001_foundation`
- `0003_demand_matching.py`: revision `0003_demand_matching`, down `0002_farmer_market`
- `0004_aggregation_commitments.py`: revision `0004_aggregation_commitments`, down `0003_demand_matching`
- `0005_orders.py`: revision `0005_orders`, down `0004_aggregation_commitments`
- `0006_logistics_delivery.py`: revision `0006_logistics_delivery`, down `0005_orders`
- `0007_payments_ledger.py`: revision `0007_payments_ledger`, down `0006_logistics_delivery`
- `0008_hardening.py`: revision `0008_hardening`, down `0007_payments_ledger`
- `0009_integrity_matching.py`: revision `0009_integrity_matching`, down `0008_hardening`
- `0010_payment_integrity.py`: revision `0010_payment_integrity`, down `0009_integrity_matching`
- `0011_idempotency_uniqueness.py`: revision `0011_idempotency_uniqueness`, down `0010_payment_integrity`
