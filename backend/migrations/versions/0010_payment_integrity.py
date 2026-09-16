"""Payment settlement integrity."""
from alembic import op
revision="0010_payment_integrity"
down_revision="0009_integrity_matching"
branch_labels=None
depends_on=None
def upgrade():
    op.create_unique_constraint("uq_payment_order_farmer","payment_intents",["order_id","farmer_id"])
def downgrade():
    op.drop_constraint("uq_payment_order_farmer","payment_intents",type_="unique")
