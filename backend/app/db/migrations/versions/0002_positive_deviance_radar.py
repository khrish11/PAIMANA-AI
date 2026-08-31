"""create positive deviance radar tables

Revision ID: 0002_positive_deviance_radar
Revises: 0001_core_tables
Create Date: 2026-08-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_positive_deviance_radar"
down_revision: str | None = "0001_core_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = "0001_core_tables"


def upgrade() -> None:
    # positive_deviants table
    op.create_table(
        "positive_deviants",
        sa.Column("deviant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reference_class_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reporting_month", sa.Date(), nullable=False),
        sa.Column("residual_cost_zscore", sa.Float(), nullable=True),
        sa.Column("residual_schedule_zscore", sa.Float(), nullable=True),
        sa.Column("data_confidence_score", sa.Float(), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reference_class_id"], ["reference_classes.class_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("deviant_id"),
    )
    op.create_index("ix_positive_deviants_project_id", "positive_deviants", ["project_id"])
    op.create_index("ix_positive_deviants_reference_class_id", "positive_deviants", ["reference_class_id"])
    op.create_index("ix_positive_deviants_reporting_month", "positive_deviants", ["reporting_month"])
    op.create_index("ix_positive_deviants_project_month", "positive_deviants", ["project_id", "reporting_month"])
    op.create_index("ix_positive_deviants_ref_class_month", "positive_deviants", ["reference_class_id", "reporting_month"])

    # extracted_actions table
    op.create_table(
        "extracted_actions",
        sa.Column("action_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deviant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_text", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("source_month", sa.String(length=20), nullable=False),
        sa.Column("quote_evidence", sa.Text(), nullable=True),
        sa.Column("specificity_score", sa.Integer(), nullable=False),
        sa.Column("llm_model_version", sa.String(length=100), nullable=True),
        sa.Column("prompt_version", sa.String(length=50), nullable=True),
        sa.Column("extracted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["deviant_id"], ["positive_deviants.deviant_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("action_id"),
    )
    op.create_index("ix_extracted_actions_deviant_id", "extracted_actions", ["deviant_id"])
    op.create_index("ix_extracted_actions_project_id", "extracted_actions", ["project_id"])
    op.create_index("ix_extracted_actions_category", "extracted_actions", ["category"])

    # playbooks table
    op.create_table(
        "playbooks",
        sa.Column("playbook_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("label", sa.String(length=500), nullable=False),
        sa.Column("confidence_tier", sa.String(length=20), nullable=False),
        sa.Column("source_action_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column("source_project_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("playbook_id"),
    )
    op.create_index("ix_playbooks_category", "playbooks", ["category"])
    op.create_index("ix_playbooks_confidence_tier", "playbooks", ["confidence_tier"])
    op.create_index("ix_playbooks_category_confidence", "playbooks", ["category", "confidence_tier"])

    # playbook_suggestions table
    op.create_table(
        "playbook_suggestions",
        sa.Column("suggestion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("playbook_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("triggered_by_risk_category", sa.String(length=50), nullable=True),
        sa.Column("suggested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("was_viewed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("was_dismissed", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["playbook_id"], ["playbooks.playbook_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("suggestion_id"),
    )
    op.create_index("ix_playbook_suggestions_project_id", "playbook_suggestions", ["project_id"])
    op.create_index("ix_playbook_suggestions_playbook_id", "playbook_suggestions", ["playbook_id"])
    op.create_index("ix_playbook_suggestions_suggested_at", "playbook_suggestions", ["suggested_at"])
    op.create_index("ix_playbook_suggestions_project_suggested", "playbook_suggestions", ["project_id", "suggested_at"])
    op.create_index("ix_playbook_suggestions_playbook_suggested", "playbook_suggestions", ["playbook_id", "suggested_at"])


def downgrade() -> None:
    op.drop_index("ix_playbook_suggestions_playbook_suggested", table_name="playbook_suggestions")
    op.drop_index("ix_playbook_suggestions_project_suggested", table_name="playbook_suggestions")
    op.drop_index("ix_playbook_suggestions_suggested_at", table_name="playbook_suggestions")
    op.drop_index("ix_playbook_suggestions_playbook_id", table_name="playbook_suggestions")
    op.drop_index("ix_playbook_suggestions_project_id", table_name="playbook_suggestions")
    op.drop_table("playbook_suggestions")

    op.drop_index("ix_playbooks_category_confidence", table_name="playbooks")
    op.drop_index("ix_playbooks_confidence_tier", table_name="playbooks")
    op.drop_index("ix_playbooks_category", table_name="playbooks")
    op.drop_table("playbooks")

    op.drop_index("ix_extracted_actions_category", table_name="extracted_actions")
    op.drop_index("ix_extracted_actions_project_id", table_name="extracted_actions")
    op.drop_index("ix_extracted_actions_deviant_id", table_name="extracted_actions")
    op.drop_table("extracted_actions")

    op.drop_index("ix_positive_deviants_ref_class_month", table_name="positive_deviants")
    op.drop_index("ix_positive_deviants_project_month", table_name="positive_deviants")
    op.drop_index("ix_positive_deviants_reporting_month", table_name="positive_deviants")
    op.drop_index("ix_positive_deviants_reference_class_id", table_name="positive_deviants")
    op.drop_index("ix_positive_deviants_project_id", table_name="positive_deviants")
    op.drop_table("positive_deviants")
