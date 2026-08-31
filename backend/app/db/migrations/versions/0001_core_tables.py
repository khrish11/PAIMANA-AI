"""create core section 6.2 tables

Revision ID: 0001_core_tables
Revises:
Create Date: 2026-08-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_core_tables"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sector", sa.String(length=120), nullable=False),
        sa.Column("ministry", sa.String(length=160), nullable=False),
        sa.Column("state", sa.String(length=120), nullable=False),
        sa.Column("sanctioned_cost", sa.Numeric(16, 2), nullable=False),
        sa.Column("approved_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("sanctioned_cost > 0", name="ck_projects_sanctioned_cost_positive"),
        sa.PrimaryKeyConstraint("project_id"),
    )
    op.create_index("ix_projects_approved_date", "projects", ["approved_date"])
    op.create_index("ix_projects_ministry", "projects", ["ministry"])
    op.create_index("ix_projects_sector", "projects", ["sector"])
    op.create_index("ix_projects_state", "projects", ["state"])
    op.create_index("ix_projects_status", "projects", ["status"])

    op.create_table(
        "reference_classes",
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sector", sa.String(length=120), nullable=False),
        sa.Column("size_band", sa.String(length=40), nullable=False),
        sa.Column("region", sa.String(length=120), nullable=False),
        sa.Column("sample_count", sa.Integer(), nullable=False),
        sa.Column("cost_overrun_p50", sa.Numeric(10, 4), nullable=True),
        sa.Column("cost_overrun_p80", sa.Numeric(10, 4), nullable=True),
        sa.Column("cost_overrun_p90", sa.Numeric(10, 4), nullable=True),
        sa.Column("schedule_delay_p50", sa.Numeric(10, 4), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("sample_count >= 0", name="ck_reference_classes_sample_count_nonnegative"),
        sa.PrimaryKeyConstraint("class_id"),
        sa.UniqueConstraint("sector", "size_band", "region", name="uq_reference_classes_cluster"),
    )

    op.create_table(
        "model_registry",
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_type", sa.String(length=80), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("trained_on_date", sa.Date(), nullable=False),
        sa.Column("validation_auc", sa.Numeric(7, 6), nullable=True),
        sa.Column("validation_f1", sa.Numeric(7, 6), nullable=True),
        sa.Column("sector_performance", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("model_id"),
        sa.UniqueConstraint("version"),
    )
    op.create_index("ix_model_registry_is_active", "model_registry", ["is_active"])
    op.create_index("ix_model_registry_model_type", "model_registry", ["model_type"])

    op.create_table(
        "cuf_submissions",
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reporting_month", sa.Date(), nullable=False),
        sa.Column("revised_cost", sa.Numeric(16, 2), nullable=True),
        sa.Column("expenditure", sa.Numeric(16, 2), nullable=True),
        sa.Column("physical_progress", sa.Numeric(5, 2), nullable=True),
        sa.Column("planned_completion", sa.Date(), nullable=True),
        sa.Column("narrative_text", sa.Text(), nullable=True),
        sa.Column("submitted_by", sa.String(length=160), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "physical_progress IS NULL OR (physical_progress >= 0 AND physical_progress <= 100)",
            name="ck_cuf_submissions_physical_progress_range",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"]),
        sa.PrimaryKeyConstraint("submission_id"),
    )
    op.create_index("ix_cuf_submissions_project_id", "cuf_submissions", ["project_id"])
    op.create_index("ix_cuf_submissions_reporting_month", "cuf_submissions", ["reporting_month"])
    op.create_index("ix_cuf_submissions_submitted_at", "cuf_submissions", ["submitted_at"])

    op.create_table(
        "predictions",
        sa.Column("prediction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_version", sa.String(length=80), nullable=False),
        sa.Column("prediction_type", sa.String(length=80), nullable=False),
        sa.Column("predicted_value", sa.Numeric(16, 4), nullable=False),
        sa.Column("confidence_interval_low", sa.Numeric(16, 4), nullable=True),
        sa.Column("confidence_interval_high", sa.Numeric(16, 4), nullable=True),
        sa.Column("shap_values", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "prediction_timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"]),
        sa.PrimaryKeyConstraint("prediction_id"),
    )
    op.create_index("ix_predictions_model_version", "predictions", ["model_version"])
    op.create_index("ix_predictions_prediction_timestamp", "predictions", ["prediction_timestamp"])
    op.create_index("ix_predictions_prediction_type", "predictions", ["prediction_type"])
    op.create_index("ix_predictions_project_id", "predictions", ["project_id"])

    op.create_table(
        "risk_scores",
        sa.Column("score_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reporting_month", sa.Date(), nullable=False),
        sa.Column("cost_risk", sa.Numeric(5, 2), nullable=False),
        sa.Column("schedule_risk", sa.Numeric(5, 2), nullable=False),
        sa.Column("progress_anomaly_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("governance_risk", sa.Numeric(5, 2), nullable=False),
        sa.Column("composite_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("risk_category", sa.String(length=40), nullable=False),
        sa.Column("data_confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("cost_risk >= 0 AND cost_risk <= 100", name="ck_risk_scores_cost_range"),
        sa.CheckConstraint("schedule_risk >= 0 AND schedule_risk <= 100", name="ck_risk_scores_schedule_range"),
        sa.CheckConstraint(
            "progress_anomaly_score >= 0 AND progress_anomaly_score <= 100",
            name="ck_risk_scores_progress_anomaly_range",
        ),
        sa.CheckConstraint(
            "governance_risk >= 0 AND governance_risk <= 100",
            name="ck_risk_scores_governance_range",
        ),
        sa.CheckConstraint("composite_score >= 0 AND composite_score <= 100", name="ck_risk_scores_composite_range"),
        sa.CheckConstraint(
            "data_confidence_score >= 0 AND data_confidence_score <= 100",
            name="ck_risk_scores_dcs_range",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"]),
        sa.PrimaryKeyConstraint("score_id"),
        sa.UniqueConstraint("project_id", "reporting_month", name="uq_risk_scores_project_month"),
    )
    op.create_index("ix_risk_scores_project_id", "risk_scores", ["project_id"])
    op.create_index("ix_risk_scores_reporting_month", "risk_scores", ["reporting_month"])
    op.create_index("ix_risk_scores_risk_category", "risk_scores", ["risk_category"])

    op.create_table(
        "nid_results",
        sa.Column("nid_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nqc_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("flagged_contradictions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("llm_model_version", sa.String(length=120), nullable=False),
        sa.CheckConstraint("nqc_score >= 0 AND nqc_score <= 100", name="ck_nid_results_nqc_score_range"),
        sa.ForeignKeyConstraint(["submission_id"], ["cuf_submissions.submission_id"]),
        sa.PrimaryKeyConstraint("nid_id"),
    )
    op.create_index("ix_nid_results_submission_id", "nid_results", ["submission_id"])

    op.create_table(
        "pbe_cohorts",
        sa.Column("cohort_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cohort_project_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column("ppi_score", sa.Numeric(7, 4), nullable=True),
        sa.Column("ppi_percentile", sa.Numeric(5, 2), nullable=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "ppi_percentile IS NULL OR (ppi_percentile >= 0 AND ppi_percentile <= 100)",
            name="ck_pbe_cohorts_ppi_percentile_range",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"]),
        sa.PrimaryKeyConstraint("cohort_id"),
    )
    op.create_index("ix_pbe_cohorts_computed_at", "pbe_cohorts", ["computed_at"])
    op.create_index("ix_pbe_cohorts_project_id", "pbe_cohorts", ["project_id"])

    op.create_table(
        "governance_actions",
        sa.Column("action_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_type", sa.String(length=80), nullable=False),
        sa.Column("triggered_by", sa.String(length=160), nullable=False),
        sa.Column("reviewed_by", sa.String(length=160), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"]),
        sa.PrimaryKeyConstraint("action_id"),
    )
    op.create_index("ix_governance_actions_project_id", "governance_actions", ["project_id"])
    op.create_index("ix_governance_actions_timestamp", "governance_actions", ["timestamp"])


def downgrade() -> None:
    op.drop_index("ix_governance_actions_timestamp", table_name="governance_actions")
    op.drop_index("ix_governance_actions_project_id", table_name="governance_actions")
    op.drop_table("governance_actions")
    op.drop_index("ix_pbe_cohorts_project_id", table_name="pbe_cohorts")
    op.drop_index("ix_pbe_cohorts_computed_at", table_name="pbe_cohorts")
    op.drop_table("pbe_cohorts")
    op.drop_index("ix_nid_results_submission_id", table_name="nid_results")
    op.drop_table("nid_results")
    op.drop_index("ix_risk_scores_risk_category", table_name="risk_scores")
    op.drop_index("ix_risk_scores_reporting_month", table_name="risk_scores")
    op.drop_index("ix_risk_scores_project_id", table_name="risk_scores")
    op.drop_table("risk_scores")
    op.drop_index("ix_predictions_project_id", table_name="predictions")
    op.drop_index("ix_predictions_prediction_type", table_name="predictions")
    op.drop_index("ix_predictions_prediction_timestamp", table_name="predictions")
    op.drop_index("ix_predictions_model_version", table_name="predictions")
    op.drop_table("predictions")
    op.drop_index("ix_cuf_submissions_submitted_at", table_name="cuf_submissions")
    op.drop_index("ix_cuf_submissions_reporting_month", table_name="cuf_submissions")
    op.drop_index("ix_cuf_submissions_project_id", table_name="cuf_submissions")
    op.drop_table("cuf_submissions")
    op.drop_index("ix_model_registry_model_type", table_name="model_registry")
    op.drop_index("ix_model_registry_is_active", table_name="model_registry")
    op.drop_table("model_registry")
    op.drop_table("reference_classes")
    op.drop_index("ix_projects_status", table_name="projects")
    op.drop_index("ix_projects_state", table_name="projects")
    op.drop_index("ix_projects_sector", table_name="projects")
    op.drop_index("ix_projects_ministry", table_name="projects")
    op.drop_index("ix_projects_approved_date", table_name="projects")
    op.drop_table("projects")
