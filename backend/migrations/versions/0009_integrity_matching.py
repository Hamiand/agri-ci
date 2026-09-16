"""Integrity fixes required by AGRI-CI-001 replacement flow."""
from alembic import op
revision="0009_integrity_matching"
down_revision="0008_hardening"
branch_labels=None
depends_on=None

def upgrade():
    op.drop_constraint("uq_aggregation_offer","aggregation_members",type_="unique")
    op.create_unique_constraint("uq_lot_source_quality_check","lot_sources",["quality_check_id"])
    op.create_unique_constraint("uq_transport_job_lot_once","transport_job_lots",["lot_id"])

def downgrade():
    op.drop_constraint("uq_transport_job_lot_once","transport_job_lots",type_="unique")
    op.drop_constraint("uq_lot_source_quality_check","lot_sources",type_="unique")
    op.create_unique_constraint("uq_aggregation_offer","aggregation_members",["aggregation_id","offer_id"])
