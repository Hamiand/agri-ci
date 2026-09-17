"""Allow multiple payment intents per farmer/order for incremental settlement.

The non-unique order/farmer lookup index already exists from migration 0007.
Migration 0010 later added a unique constraint on the same columns. Removing
that constraint is therefore sufficient to permit incremental settlement while
retaining the original lookup index.
"""
from alembic import op

revision="0014_incremental_payment_intents"
down_revision="0013_payment_settlement_quantity"
branch_labels=None
depends_on=None


def upgrade():
    op.drop_constraint("uq_payment_order_farmer","payment_intents",type_="unique")


def downgrade():
    # A database that has already stored multiple settlement tranches must
    # consolidate them before this downgrade can restore the old uniqueness
    # rule. PostgreSQL will reject the downgrade rather than silently lose data.
    op.create_unique_constraint("uq_payment_order_farmer","payment_intents",["order_id","farmer_id"])
