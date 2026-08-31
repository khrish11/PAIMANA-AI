"""Add notes column to governance_actions table

Revision ID: 0003_governance_notes
Revises: 0002_positive_deviance_radar
Create Date: 2026-08-31

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003_governance_notes'
down_revision = '0002_positive_deviance_radar'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add notes column to governance_actions table
    op.add_column('governance_actions', sa.Column('notes', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove notes column from governance_actions table
    op.drop_column('governance_actions', 'notes')
