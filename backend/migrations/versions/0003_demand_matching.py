"""Buyer, demand and matching tables."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_demand_matching"
down_revision = "0002_farmer_market"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("buyers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("buyer_ref", sa.String(40), nullable=False, unique=True),
        sa.Column("display_name", sa.String(180), nullable=False),
        sa.Column("buyer_type", sa.String(30), nullable=False),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("reliability_score", sa.Numeric(5,2), nullable=False, server_default="70"),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("reliability_score >= 0 AND reliability_score <= 100", name="ck_buyer_reliability"),
    )
    op.create_table("demands",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("demand_ref", sa.String(40), nullable=False, unique=True),
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buyers.id"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity_required_kg", sa.Numeric(14,3), nullable=False),
        sa.Column("delivery_start_date", sa.Date(), nullable=False),
        sa.Column("delivery_end_date", sa.Date(), nullable=False),
        sa.Column("target_price_xof_per_kg", sa.Numeric(14,2), nullable=True),
        sa.Column("quality_grades", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("destination_city", sa.String(100), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="PUBLISHED"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("quantity_required_kg > 0", name="ck_demand_qty_positive"),
        sa.CheckConstraint("delivery_end_date >= delivery_start_date", name="ck_demand_dates"),
    )
    op.create_table("matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("demand_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("demands.id", ondelete="CASCADE"), nullable=False),
        sa.Column("offer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("offers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("compatible_quantity_kg", sa.Numeric(14,3), nullable=False),
        sa.Column("date_score", sa.Numeric(5,2), nullable=False),
        sa.Column("price_score", sa.Numeric(5,2), nullable=False),
        sa.Column("logistics_score", sa.Numeric(5,2), nullable=False),
        sa.Column("quality_score", sa.Numeric(5,2), nullable=False),
        sa.Column("reliability_score", sa.Numeric(5,2), nullable=False),
        sa.Column("volume_score", sa.Numeric(5,2), nullable=False),
        sa.Column("total_score", sa.Numeric(5,2), nullable=False),
        sa.Column("explanation", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("demand_id", "offer_id", name="uq_match_demand_offer"),
        sa.CheckConstraint("compatible_quantity_kg > 0", name="ck_match_qty_positive"),
        sa.CheckConstraint("date_score between 0 and 100 AND price_score between 0 and 100 AND logistics_score between 0 and 100 AND quality_score between 0 and 100 AND reliability_score between 0 and 100 AND volume_score between 0 and 100 AND total_score between 0 and 100", name="ck_match_scores"),
    )
    op.create_index("ix_demands_product_status", "demands", ["product_id","status"])
    op.create_index("ix_matches_demand_score", "matches", ["demand_id","total_score"])

def downgrade():
    op.drop_index("ix_matches_demand_score", table_name="matches")
    op.drop_index("ix_demands_product_status", table_name="demands")
    op.drop_table("matches")
    op.drop_table("demands")
    op.drop_table("buyers")
