# AGRI-CI Quantity Concurrency Proof

The production primitive `reserve_available_quantity()` locks the selected offer with
PostgreSQL `SELECT ... FOR UPDATE`.

The integration test starts two independent SQLAlchemy sessions and two threads.
Both request Koffi's same 400 kg after a synchronization barrier.

Expected and asserted result:
- exactly one transaction: SUCCESS
- exactly one transaction: INSUFFICIENT
- final available: 0 kg
- final reserved: 400 kg
- offer version increments once

This is a genuine PostgreSQL race test when `TEST_DATABASE_URL` points to PostgreSQL.
The GitHub Actions workflow provisions PostgreSQL 16 and runs the integration directory
after `alembic upgrade head`.
