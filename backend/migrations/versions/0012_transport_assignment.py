"""Assign transport jobs to authenticated transporter users."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision="0012_transport_assignment"
down_revision="0011_idempotency_uniqueness"
branch_labels=None
depends_on=None

def upgrade():
    op.add_column("transport_jobs",sa.Column("transporter_user_id",postgresql.UUID(as_uuid=True),nullable=True))
    op.create_foreign_key("fk_transport_jobs_transporter_user","transport_jobs","users",["transporter_user_id"],["id"])
    op.create_index("ix_transport_jobs_transporter_user_id","transport_jobs",["transporter_user_id"])

def downgrade():
    op.drop_index("ix_transport_jobs_transporter_user_id",table_name="transport_jobs")
    op.drop_constraint("fk_transport_jobs_transporter_user","transport_jobs",type_="foreignkey")
    op.drop_column("transport_jobs","transporter_user_id")
