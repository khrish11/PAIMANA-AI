"""Fix audit_log column sizes for UUIDs

Revision ID: 0005_fix_audit_log_sizes
Revises: 0004_audit_log
Create Date: 2026-08-31

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0005_fix_audit_log_sizes'
down_revision = '0004_audit_log'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop and recreate audit_log table with correct column sizes
    op.drop_table('audit_log')
    
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
    # Revert to original schema
    op.drop_table('audit_log')
    
    op.create_table(
        'audit_log',
        sa.Column('audit_id', sa.String(32), primary_key=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
        sa.Column('user', sa.String(160), nullable=False),
        sa.Column('role', sa.String(80), nullable=False),
        sa.Column('action', sa.String(80), nullable=False, index=True),
        sa.Column('entity_type', sa.String(80), nullable=False, index=True),
        sa.Column('entity_id', sa.String(32), nullable=False, index=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('before_summary', sa.Text(), nullable=True),
        sa.Column('after_summary', sa.Text(), nullable=True)
    )
