"""Payment intents, deductions and immutable ledger."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0007_payments_ledger"
down_revision="0006_logistics_delivery"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("payment_intents",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("payment_ref",sa.String(40),nullable=False,unique=True),
      sa.Column("order_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("orders.id"),nullable=False),
      sa.Column("farmer_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("farmers.id"),nullable=False),
      sa.Column("gross_amount_xof",sa.Numeric(16,2),nullable=False),
      sa.Column("deductions_xof",sa.Numeric(16,2),nullable=False,server_default="0"),
      sa.Column("net_amount_xof",sa.Numeric(16,2),nullable=False),
      sa.Column("currency",sa.String(3),nullable=False,server_default="XOF"),
      sa.Column("provider",sa.String(50),nullable=False),
      sa.Column("provider_reference",sa.String(120),nullable=True,unique=True),
      sa.Column("status",sa.String(30),nullable=False,server_default="PENDING"),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
      sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False),
      sa.CheckConstraint("gross_amount_xof >= 0 AND deductions_xof >= 0 AND net_amount_xof >= 0",name="ck_payment_amounts"),
      sa.CheckConstraint("net_amount_xof = gross_amount_xof - deductions_xof",name="ck_payment_net"))
    op.create_table("payment_deductions",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("payment_intent_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("payment_intents.id",ondelete="CASCADE"),nullable=False),
      sa.Column("deduction_type",sa.String(40),nullable=False),
      sa.Column("description",sa.String(200),nullable=False),
      sa.Column("amount_xof",sa.Numeric(16,2),nullable=False),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
      sa.CheckConstraint("amount_xof >= 0",name="ck_deduction_amount"))
    op.create_table("ledger_entries",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("entry_ref",sa.String(40),nullable=False,unique=True),
      sa.Column("payment_intent_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("payment_intents.id"),nullable=False),
      sa.Column("entry_type",sa.String(30),nullable=False),
      sa.Column("amount_xof",sa.Numeric(16,2),nullable=False),
      sa.Column("currency",sa.String(3),nullable=False,server_default="XOF"),
      sa.Column("description",sa.String(240),nullable=False),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
      sa.CheckConstraint("amount_xof >= 0",name="ck_ledger_amount"))
    op.create_index("ix_payment_order_farmer","payment_intents",["order_id","farmer_id"])
    op.create_index("ix_ledger_payment","ledger_entries",["payment_intent_id"])

def downgrade():
    op.drop_index("ix_ledger_payment",table_name="ledger_entries")
    op.drop_index("ix_payment_order_farmer",table_name="payment_intents")
    op.drop_table("ledger_entries")
    op.drop_table("payment_deductions")
    op.drop_table("payment_intents")
