"""Farmer, farm, plot, product, harvest and offer tables."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_farmer_market"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("farmers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("farmer_ref", sa.String(30), nullable=False, unique=True),
        sa.Column("display_name", sa.String(150), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="VERIFIED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table("farms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("locality", sa.String(150), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table("plots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plot_ref", sa.String(40), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("area_ha", sa.Numeric(12,3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("farm_id", "plot_ref", name="uq_plot_ref_per_farm"),
        sa.CheckConstraint("area_ha > 0", name="ck_plot_area_positive"),
    )
    op.create_table("products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name_fr", sa.String(100), nullable=False),
        sa.Column("name_en", sa.String(100), nullable=False),
        sa.Column("default_unit", sa.String(20), nullable=False, server_default="kg"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table("harvests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("harvest_ref", sa.String(40), nullable=False, unique=True),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmers.id"), nullable=False),
        sa.Column("plot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plots.id"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("expected_start_date", sa.Date(), nullable=False),
        sa.Column("expected_end_date", sa.Date(), nullable=False),
        sa.Column("estimated_quantity_kg", sa.Numeric(14,3), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="FORECAST"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("estimated_quantity_kg > 0", name="ck_harvest_qty_positive"),
        sa.CheckConstraint("expected_end_date >= expected_start_date", name="ck_harvest_dates"),
    )
    op.create_table("harvest_forecasts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("harvest_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("harvests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("revision_no", sa.Integer(), nullable=False),
        sa.Column("estimated_quantity_kg", sa.Numeric(14,3), nullable=False),
        sa.Column("expected_start_date", sa.Date(), nullable=False),
        sa.Column("expected_end_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("harvest_id", "revision_no", name="uq_harvest_forecast_revision"),
    )
    op.create_table("offers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("offer_ref", sa.String(40), nullable=False, unique=True),
        sa.Column("harvest_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("harvests.id"), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmers.id"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity_total_kg", sa.Numeric(14,3), nullable=False),
        sa.Column("quantity_available_kg", sa.Numeric(14,3), nullable=False),
        sa.Column("quantity_proposed_kg", sa.Numeric(14,3), nullable=False, server_default="0"),
        sa.Column("quantity_reserved_kg", sa.Numeric(14,3), nullable=False, server_default="0"),
        sa.Column("quantity_sold_kg", sa.Numeric(14,3), nullable=False, server_default="0"),
        sa.Column("asking_price_xof_per_kg", sa.Numeric(14,2), nullable=True),
        sa.Column("quality_grade", sa.String(20), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="DRAFT"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("quantity_total_kg > 0", name="ck_offer_total_positive"),
        sa.CheckConstraint("quantity_available_kg >= 0 AND quantity_proposed_kg >= 0 AND quantity_reserved_kg >= 0 AND quantity_sold_kg >= 0", name="ck_offer_qty_nonnegative"),
        sa.CheckConstraint("quantity_available_kg + quantity_proposed_kg + quantity_reserved_kg + quantity_sold_kg = quantity_total_kg", name="ck_offer_qty_balance"),
    )
    products = sa.table("products",
        sa.column("id", postgresql.UUID(as_uuid=True)), sa.column("code", sa.String),
        sa.column("name_fr", sa.String), sa.column("name_en", sa.String),
        sa.column("default_unit", sa.String), sa.column("active", sa.Boolean))
    import uuid
    op.bulk_insert(products, [
        {"id": uuid.uuid4(), "code":"TOM","name_fr":"Tomate","name_en":"Tomato","default_unit":"kg","active":True},
        {"id": uuid.uuid4(), "code":"MAN","name_fr":"Mangue","name_en":"Mango","default_unit":"kg","active":True},
        {"id": uuid.uuid4(), "code":"AVO","name_fr":"Avocat","name_en":"Avocado","default_unit":"kg","active":True},
        {"id": uuid.uuid4(), "code":"CASS","name_fr":"Manioc","name_en":"Cassava","default_unit":"kg","active":True},
        {"id": uuid.uuid4(), "code":"YAM","name_fr":"Igname","name_en":"Yam","default_unit":"kg","active":True},
        {"id": uuid.uuid4(), "code":"BAN","name_fr":"Banane","name_en":"Banana","default_unit":"kg","active":True},
    ])

def downgrade():
    for table in ["offers","harvest_forecasts","harvests","plots","farms","farmers","products"]:
        op.drop_table(table)
