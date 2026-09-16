"""Hardening: idempotency keys."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0008_hardening"
down_revision="0007_payments_ledger"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("idempotency_keys",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("user_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),
      sa.Column("endpoint",sa.String(200),nullable=False),
      sa.Column("key",sa.String(120),nullable=False),
      sa.Column("request_hash",sa.String(64),nullable=False),
      sa.Column("response_status",sa.Integer(),nullable=True),
      sa.Column("response_body",postgresql.JSONB(),nullable=True),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
      sa.UniqueConstraint("user_id","endpoint","key",name="uq_idempotency_scope"))
def downgrade():
    op.drop_table("idempotency_keys")
