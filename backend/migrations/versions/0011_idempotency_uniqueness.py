"""Persisted idempotency uniqueness."""
from alembic import op
revision="0011_idempotency_uniqueness"
down_revision="0010_payment_integrity"
branch_labels=None
depends_on=None
def upgrade():
    op.create_unique_constraint("uq_idempotency_user_endpoint_key","idempotency_keys",["user_id","endpoint","key"])
def downgrade():
    op.drop_constraint("uq_idempotency_user_endpoint_key","idempotency_keys",type_="unique")
