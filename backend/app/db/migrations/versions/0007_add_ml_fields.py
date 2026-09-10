"""Add ML prediction fields to risk_scores table

Revision ID: 0007_add_ml_fields
Revises: 0006_continuous_operations
Create Date: 2026-09-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0007_add_ml_fields'
down_revision = '0006_continuous_operations'
branch_labels = None
depends_on = None


def upgrade():
    """Add ML prediction fields to risk_scores table."""
    op.add_column('risk_scores', sa.Column('ml_cost_risk', sa.Numeric(5, 2), nullable=True))
    op.add_column('risk_scores', sa.Column('ml_schedule_risk', sa.Numeric(5, 2), nullable=True))
    op.add_column('risk_scores', sa.Column('ml_cost_probability', sa.Numeric(5, 4), nullable=True))
    op.add_column('risk_scores', sa.Column('ml_schedule_probability', sa.Numeric(5, 4), nullable=True))
    op.add_column('risk_scores', sa.Column('ml_model_version', sa.String(80), nullable=True))
    op.add_column('risk_scores', sa.Column('ml_model_status', sa.String(40), nullable=True))
    op.add_column('risk_scores', sa.Column('shap_drivers', postgresql.JSONB(), nullable=True))


def downgrade():
    """Remove ML prediction fields from risk_scores table."""
    op.drop_column('risk_scores', 'shap_drivers')
    op.drop_column('risk_scores', 'ml_model_status')
    op.drop_column('risk_scores', 'ml_model_version')
    op.drop_column('risk_scores', 'ml_schedule_probability')
    op.drop_column('risk_scores', 'ml_cost_probability')
    op.drop_column('risk_scores', 'ml_schedule_risk')
    op.drop_column('risk_scores', 'ml_cost_risk')
