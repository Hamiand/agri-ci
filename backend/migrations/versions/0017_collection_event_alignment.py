"""Align collection event persistence with the current domain model.

The allocation is the source of truth for the quantity announced/committed by the
farmer.  A collection event records only what was physically received.  Keeping a
second announced quantity on every partial collection duplicates state and can
become inconsistent with the order allocation.
"""
from alembic import op
import sqlalchemy as sa

revision="0017_collection_event_alignment"
down_revision="0016_outbox_delivery_tracking"
branch_labels=None
depends_on=None


def upgrade():
    op.drop_constraint("ck_collection_qty_positive","collection_events",type_="check")
    op.drop_column("collection_events","announced_quantity_kg")
    op.drop_column("collection_events","status")
    op.create_check_constraint(
        "ck_collection_received_qty_positive",
        "collection_events",
        "received_quantity_kg > 0",
    )


def downgrade():
    op.drop_constraint("ck_collection_received_qty_positive","collection_events",type_="check")
    op.add_column(
        "collection_events",
        sa.Column("announced_quantity_kg",sa.Numeric(14,3),nullable=True),
    )
    op.execute("UPDATE collection_events SET announced_quantity_kg = received_quantity_kg")
    op.alter_column("collection_events","announced_quantity_kg",nullable=False)
    op.add_column(
        "collection_events",
        sa.Column("status",sa.String(30),nullable=False,server_default="RECEIVED"),
    )
    op.create_check_constraint(
        "ck_collection_qty_positive",
        "collection_events",
        "announced_quantity_kg > 0 AND received_quantity_kg > 0",
    )
