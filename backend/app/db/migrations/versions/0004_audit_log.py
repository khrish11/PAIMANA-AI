"""Create audit_log table for persistent audit trails

Revision ID: 0004_audit_log
Revises: 0003_governance_notes
Create Date: 2026-08-31

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004_audit_log'
down_revision = '0003_governance_notes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create audit_log table
    op.create_table(
        'audit_log',
        sa.Column('audit_id', sa.String(36), primary_key=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
        sa.Column('user', sa.String(160), nullable=False),
        sa.Column('role', sa.String(80), nullable=False),
        sa.Column('action', sa.String(80), nullable=False, index=True),
        sa.Column('entity_type', sa.String(80), nullable=False, index=True),
        sa.Column('entity_id', sa.String(36), nullable=False, index=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('before_summary', sa.Text(), nullable=True),
        sa.Column('after_summary', sa.Text(), nullable=True)
    )


def downgrade() -> None:
    # Drop audit_log table
    op.drop_table('audit_log')
