"""Orders and allocations."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision="0005_orders"
down_revision="0004_aggregation_commitments"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("orders",
        sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
        sa.Column("order_ref",sa.String(40),nullable=False,unique=True),
        sa.Column("aggregation_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("aggregations.id"),nullable=False,unique=True),
        sa.Column("demand_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("demands.id"),nullable=False),
        sa.Column("buyer_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("buyers.id"),nullable=False),
        sa.Column("product_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("products.id"),nullable=False),
        sa.Column("quantity_kg",sa.Numeric(14,3),nullable=False),
        sa.Column("status",sa.String(30),nullable=False,server_default="CONFIRMED"),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.CheckConstraint("quantity_kg > 0",name="ck_order_qty_positive"),
    )
    op.create_table("order_allocations",
        sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
        sa.Column("order_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("orders.id",ondelete="CASCADE"),nullable=False),
        sa.Column("offer_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("offers.id"),nullable=False),
        sa.Column("farmer_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("farmers.id"),nullable=False),
        sa.Column("quantity_kg",sa.Numeric(14,3),nullable=False),
        sa.Column("status",sa.String(30),nullable=False,server_default="ALLOCATED"),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.CheckConstraint("quantity_kg > 0",name="ck_order_allocation_qty_positive"),
    )
    op.create_index("ix_order_allocations_order","order_allocations",["order_id"])

def downgrade():
    op.drop_index("ix_order_allocations_order",table_name="order_allocations")
    op.drop_table("order_allocations")
    op.drop_table("orders")
