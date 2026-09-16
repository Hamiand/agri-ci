"""Run with a PostgreSQL test database after `alembic upgrade head`."""
from sqlalchemy import inspect
from app.database.session import engine

REQUIRED_TABLES={
    "users","farmers","farms","plots","products","harvests","harvest_forecasts","offers",
    "buyers","demands","matches","aggregations","aggregation_members","commitments",
    "orders","order_allocations","collection_events","quality_checks","lots","lot_sources",
    "transport_jobs","transport_job_lots","deliveries","payment_intents","payment_deductions",
    "ledger_entries","domain_events","idempotency_keys"
}
def test_required_tables_exist():
    tables=set(inspect(engine).get_table_names())
    assert REQUIRED_TABLES <= tables
