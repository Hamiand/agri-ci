"""Collection, quality, lots, transport and delivery."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0006_logistics_delivery"
down_revision="0005_orders"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("collection_events",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("collection_ref",sa.String(40),nullable=False,unique=True),
      sa.Column("order_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("orders.id"),nullable=False),
      sa.Column("order_allocation_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("order_allocations.id"),nullable=False),
      sa.Column("farmer_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("farmers.id"),nullable=False),
      sa.Column("announced_quantity_kg",sa.Numeric(14,3),nullable=False),
      sa.Column("received_quantity_kg",sa.Numeric(14,3),nullable=False),
      sa.Column("location_name",sa.String(180),nullable=True),
      sa.Column("status",sa.String(30),nullable=False,server_default="RECEIVED"),
      sa.Column("collected_at",sa.DateTime(timezone=True),nullable=False),
      sa.CheckConstraint("announced_quantity_kg > 0 AND received_quantity_kg > 0",name="ck_collection_qty_positive"))
    op.create_table("quality_checks",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("collection_event_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("collection_events.id",ondelete="CASCADE"),nullable=False),
      sa.Column("grade",sa.String(10),nullable=False),
      sa.Column("quantity_kg",sa.Numeric(14,3),nullable=False),
      sa.Column("notes",sa.Text(),nullable=True),
      sa.Column("checked_at",sa.DateTime(timezone=True),nullable=False),
      sa.CheckConstraint("quantity_kg > 0",name="ck_quality_qty_positive"))
    op.create_table("lots",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("lot_ref",sa.String(40),nullable=False,unique=True),
      sa.Column("order_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("orders.id"),nullable=False),
      sa.Column("product_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("products.id"),nullable=False),
      sa.Column("grade",sa.String(10),nullable=False),
      sa.Column("quantity_kg",sa.Numeric(14,3),nullable=False),
      sa.Column("status",sa.String(30),nullable=False,server_default="READY"),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
      sa.CheckConstraint("quantity_kg > 0",name="ck_lot_qty_positive"))
    op.create_table("lot_sources",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("lot_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("lots.id",ondelete="CASCADE"),nullable=False),
      sa.Column("quality_check_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("quality_checks.id"),nullable=False),
      sa.Column("quantity_kg",sa.Numeric(14,3),nullable=False),
      sa.CheckConstraint("quantity_kg > 0",name="ck_lot_source_qty_positive"))
    op.create_table("transport_jobs",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("transport_ref",sa.String(40),nullable=False,unique=True),
      sa.Column("order_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("orders.id"),nullable=False),
      sa.Column("origin",sa.String(180),nullable=False),
      sa.Column("destination",sa.String(180),nullable=False),
      sa.Column("vehicle_ref",sa.String(100),nullable=True),
      sa.Column("driver_name",sa.String(150),nullable=True),
      sa.Column("status",sa.String(30),nullable=False,server_default="PLANNED"),
      sa.Column("departed_at",sa.DateTime(timezone=True),nullable=True),
      sa.Column("arrived_at",sa.DateTime(timezone=True),nullable=True),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("transport_job_lots",
      sa.Column("transport_job_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("transport_jobs.id",ondelete="CASCADE"),primary_key=True),
      sa.Column("lot_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("lots.id"),primary_key=True))
    op.create_table("deliveries",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("delivery_ref",sa.String(40),nullable=False,unique=True),
      sa.Column("order_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("orders.id"),nullable=False),
      sa.Column("transport_job_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("transport_jobs.id"),nullable=False),
      sa.Column("delivered_quantity_kg",sa.Numeric(14,3),nullable=False),
      sa.Column("received_by",sa.String(150),nullable=False),
      sa.Column("status",sa.String(30),nullable=False,server_default="DELIVERED"),
      sa.Column("delivered_at",sa.DateTime(timezone=True),nullable=False),
      sa.CheckConstraint("delivered_quantity_kg > 0",name="ck_delivery_qty_positive"))
    op.create_index("ix_collection_order","collection_events",["order_id"])
    op.create_index("ix_lots_order","lots",["order_id"])
    op.create_index("ix_transport_order","transport_jobs",["order_id"])

def downgrade():
    for idx,table in [("ix_transport_order","transport_jobs"),("ix_lots_order","lots"),("ix_collection_order","collection_events")]:
        op.drop_index(idx,table_name=table)
    for table in ["deliveries","transport_job_lots","transport_jobs","lot_sources","lots","quality_checks","collection_events"]:
        op.drop_table(table)
