"""AGRI-CI foundation tables"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("phone", sa.String(30), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("preferred_language", sa.String(10), nullable=False, server_default="fr"),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)
    op.create_table("roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
    )
    op.create_table("user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table("audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(100), nullable=True),
        sa.Column("request_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    roles = sa.table("roles", sa.column("name", sa.String))
    op.bulk_insert(roles, [{"name": x} for x in [
        "FARMER","BUYER","PRO_BUYER","AGENT","COLLECTION_AGENT","TRANSPORTER",
        "COOPERATIVE_MANAGER","OPERATIONS_MANAGER","ADMIN"
    ]])

def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("user_roles")
    op.drop_table("roles")
    op.drop_index("ix_users_phone", table_name="users")
    op.drop_table("users")
