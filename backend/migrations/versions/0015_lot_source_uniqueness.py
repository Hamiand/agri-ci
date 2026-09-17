"""Prevent one quality check from being assigned to multiple lots.

The API already treats a quality check as a single-use source.  Enforcing that
rule in PostgreSQL closes the concurrent-request race as well.
"""
from alembic import op

revision="0015_lot_source_uniqueness"
down_revision="0014_incremental_payment_intents"
branch_labels=None
depends_on=None


def upgrade():
    op.create_unique_constraint(
        "uq_lot_source_quality_check",
        "lot_sources",
        ["quality_check_id"],
    )


def downgrade():
    op.drop_constraint(
        "uq_lot_source_quality_check",
        "lot_sources",
        type_="unique",
    )
