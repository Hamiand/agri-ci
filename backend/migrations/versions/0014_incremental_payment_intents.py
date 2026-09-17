"""Allow multiple payment intents per farmer/order for incremental settlement.

Idempotency and the order row lock protect duplicate settlement preparation;
settled_quantity_kg records the quantity represented by each tranche.
"""
from alembic import op

revision="0014_incremental_payment_intents"
down_revision="0013_payment_settlement_quantity"
branch_labels=None
depends_on=None


def upgrade():
    op.drop_constraint("uq_payment_order_farmer","payment_intents",type_="unique")
    op.create_index("ix_payment_order_farmer","payment_intents",["order_id","farmer_id"],unique=False)


def downgrade():
    op.drop_index("ix_payment_order_farmer",table_name="payment_intents")
    # Downgrade is intentionally conservative: a database that has already
    # stored multiple settlement tranches must consolidate them before the old
    # one-payment-per-farmer uniqueness rule can safely be restored.
    op.create_unique_constraint("uq_payment_order_farmer","payment_intents",["order_id","farmer_id"])
