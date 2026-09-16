"""Aggregation, commitments and transactional outbox."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision="0004_aggregation_commitments"
down_revision="0003_demand_matching"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("aggregations",
        sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
        sa.Column("aggregation_ref",sa.String(40),nullable=False,unique=True),
        sa.Column("demand_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("demands.id",ondelete="CASCADE"),nullable=False),
        sa.Column("target_quantity_kg",sa.Numeric(14,3),nullable=False),
        sa.Column("proposed_quantity_kg",sa.Numeric(14,3),nullable=False,server_default="0"),
        sa.Column("accepted_quantity_kg",sa.Numeric(14,3),nullable=False,server_default="0"),
        sa.Column("status",sa.String(30),nullable=False,server_default="PROPOSING"),
        sa.Column("version",sa.Integer(),nullable=False,server_default="1"),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.CheckConstraint("target_quantity_kg > 0 AND proposed_quantity_kg >= 0 AND accepted_quantity_kg >= 0",name="ck_aggregation_qty"),
    )
    op.create_table("aggregation_members",
        sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
        sa.Column("aggregation_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("aggregations.id",ondelete="CASCADE"),nullable=False),
        sa.Column("offer_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("offers.id"),nullable=False),
        sa.Column("proposed_quantity_kg",sa.Numeric(14,3),nullable=False),
        sa.Column("accepted_quantity_kg",sa.Numeric(14,3),nullable=False,server_default="0"),
        sa.Column("status",sa.String(30),nullable=False,server_default="PROPOSED"),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint("aggregation_id","offer_id",name="uq_aggregation_offer"),
    )
    op.create_table("commitments",
        sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
        sa.Column("commitment_ref",sa.String(40),nullable=False,unique=True),
        sa.Column("aggregation_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("aggregations.id",ondelete="CASCADE"),nullable=False),
        sa.Column("aggregation_member_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("aggregation_members.id",ondelete="CASCADE"),nullable=False,unique=True),
        sa.Column("offer_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("offers.id"),nullable=False),
        sa.Column("farmer_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("farmers.id"),nullable=False),
        sa.Column("quantity_kg",sa.Numeric(14,3),nullable=False),
        sa.Column("status",sa.String(20),nullable=False,server_default="PENDING"),
        sa.Column("expires_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("responded_at",sa.DateTime(timezone=True),nullable=True),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.CheckConstraint("quantity_kg > 0",name="ck_commitment_qty_positive"),
    )
    op.create_table("domain_events",
        sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
        sa.Column("event_type",sa.String(100),nullable=False),
        sa.Column("aggregate_type",sa.String(100),nullable=False),
        sa.Column("aggregate_id",sa.String(100),nullable=False),
        sa.Column("payload",postgresql.JSONB(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("published_at",sa.DateTime(timezone=True),nullable=True),
    )
    op.create_index("ix_commitments_farmer_status","commitments",["farmer_id","status"])
    op.create_index("ix_domain_events_unpublished","domain_events",["published_at"])

def downgrade():
    op.drop_index("ix_domain_events_unpublished",table_name="domain_events")
    op.drop_index("ix_commitments_farmer_status",table_name="commitments")
    op.drop_table("domain_events")
    op.drop_table("commitments")
    op.drop_table("aggregation_members")
    op.drop_table("aggregations")
