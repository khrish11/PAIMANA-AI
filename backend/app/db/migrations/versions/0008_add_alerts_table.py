"""Add alerts table for early warning system

Revision ID: 0008_add_alerts
Revises: 0007_add_ml_fields
Create Date: 2026-09-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0008_add_alerts'
down_revision = '0007_add_ml_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add alerts table for early warning system."""
    op.create_table(
        'alerts',
        sa.Column('alert_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('alert_type', sa.String(80), nullable=False, index=True),
        sa.Column('severity', sa.String(20), nullable=False, index=True),
        sa.Column('trigger', sa.Text(), nullable=False),
        sa.Column('evidence', postgresql.JSONB(), nullable=False),
        sa.Column('reporting_month', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='OPEN', index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acknowledged_by', sa.String(160), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.String(160), nullable=True),
    )


def downgrade():
    """Remove alerts table."""
    op.drop_table('alerts')
