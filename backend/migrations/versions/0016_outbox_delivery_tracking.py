"""Track transactional outbox delivery attempts.

Revision ID: 0016_outbox_delivery_tracking
Revises: 0015_lot_source_uniqueness
"""
from alembic import op
import sqlalchemy as sa

revision = "0016_outbox_delivery_tracking"
down_revision = "0015_lot_source_uniqueness"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("domain_events", sa.Column("publish_attempts", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("domain_events", sa.Column("last_publish_error", sa.Text(), nullable=True))
    op.add_column("domain_events", sa.Column("last_publish_attempt_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column("domain_events", "last_publish_attempt_at")
    op.drop_column("domain_events", "last_publish_error")
    op.drop_column("domain_events", "publish_attempts")
