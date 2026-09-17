"""Document the existing lot-source uniqueness invariant.

The database constraint uq_lot_source_quality_check was introduced by migration
0009_integrity_matching.  The API hardening added later locks quality checks
with FOR UPDATE and rejects duplicate IDs in a request.  No schema mutation is
needed here; keeping this revision as a no-op preserves the Alembic chain and
avoids trying to recreate the existing PostgreSQL constraint.
"""

revision="0015_lot_source_uniqueness"
down_revision="0014_incremental_payment_intents"
branch_labels=None
depends_on=None


def upgrade():
    pass


def downgrade():
    pass
