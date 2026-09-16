"""Track the delivered quantity represented by each payment intent."""
from alembic import op
import sqlalchemy as sa

revision="0013_payment_settlement_quantity"
down_revision="0012_transport_assignment"
branch_labels=None
depends_on=None

def upgrade():
    op.add_column("payment_intents",sa.Column("settled_quantity_kg",sa.Numeric(14,3),nullable=True))
    # Existing payment rows predate tranche settlement tracking. They remain
    # readable; new settlement-generated payments always populate this field.

def downgrade():
    op.drop_column("payment_intents","settled_quantity_kg")
