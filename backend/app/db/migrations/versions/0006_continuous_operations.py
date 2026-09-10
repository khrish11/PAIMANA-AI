"""Add continuous operations support: revisions, provenance, project metadata

Revision ID: 0006_continuous_operations
Revises: 0005_fix_audit_log_sizes
Create Date: 2026-09-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_continuous_operations"
down_revision: str | None = "0005_fix_audit_log_sizes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add project metadata fields
    op.add_column('projects', sa.Column('project_name', sa.String(length=200), nullable=True))
    op.add_column('projects', sa.Column('project_code', sa.String(length=50), nullable=True, unique=True))
    op.add_column('projects', sa.Column('department', sa.String(length=160), nullable=True))
    op.add_column('projects', sa.Column('implementing_agency', sa.String(length=160), nullable=True))
    op.add_column('projects', sa.Column('original_completion_date', sa.Date(), nullable=True))
    op.add_column('projects', sa.Column('revised_completion_date', sa.Date(), nullable=True))
    op.add_column('projects', sa.Column('data_source', sa.String(length=80), nullable=True, server_default='manual'))
    op.add_column('projects', sa.Column('source_file', sa.String(length=255), nullable=True))
    op.add_column('projects', sa.Column('source_date', sa.Date(), nullable=True))
    op.add_column('projects', sa.Column('entered_by', sa.String(length=160), nullable=True))
    op.add_column('projects', sa.Column('import_method', sa.String(length=80), nullable=True, server_default='manual'))
    op.add_column('projects', sa.Column('provenance_status', sa.String(length=40), nullable=True, server_default='verified'))
    
    # Add index on project_code
    op.create_index('ix_projects_project_code', 'projects', ['project_code'])
    
    # Add versioning and provenance to CUF submissions
    op.add_column('cuf_submissions', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('cuf_submissions', sa.Column('is_latest', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('cuf_submissions', sa.Column('superseded_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('cuf_submissions', sa.Column('superseded_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('cuf_submissions', sa.Column('superseded_reason', sa.Text(), nullable=True))
    op.add_column('cuf_submissions', sa.Column('data_source', sa.String(length=80), nullable=True, server_default='manual'))
    op.add_column('cuf_submissions', sa.Column('source_file', sa.String(length=255), nullable=True))
    op.add_column('cuf_submissions', sa.Column('source_date', sa.Date(), nullable=True))
    op.add_column('cuf_submissions', sa.Column('import_method', sa.String(length=80), nullable=True, server_default='manual'))
    op.add_column('cuf_submissions', sa.Column('provenance_status', sa.String(length=40), nullable=True, server_default='verified'))
    
    # Add foreign key for superseded_by
    op.create_foreign_key('fk_cuf_submissions_superseded_by', 'cuf_submissions', 'cuf_submissions', ['superseded_by'], ['submission_id'])
    
    # Add index on is_latest
    op.create_index('ix_cuf_submissions_is_latest', 'cuf_submissions', ['is_latest'])
    
    # Create revisions table for tracking changes
    op.create_table(
        'cuf_revisions',
        sa.Column('revision_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('revision_number', sa.Integer(), nullable=False),
        sa.Column('field_name', sa.String(length=80), nullable=False),
        sa.Column('previous_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('actor', sa.String(length=160), nullable=False),
        sa.Column('actor_role', sa.String(length=80), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('request_id', sa.String(length=80), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["cuf_submissions.submission_id"]),
        sa.PrimaryKeyConstraint("revision_id"),
    )
    op.create_index('ix_cuf_revisions_submission_id', 'cuf_revisions', ['submission_id'])
    op.create_index('ix_cuf_revisions_timestamp', 'cuf_revisions', ['timestamp'])
    
    # Create import_batches table for tracking bulk imports
    op.create_table(
        'import_batches',
        sa.Column('batch_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('batch_name', sa.String(length=200), nullable=False),
        sa.Column('import_method', sa.String(length=80), nullable=False),
        sa.Column('source_file', sa.String(length=255), nullable=True),
        sa.Column('rows_detected', sa.Integer(), nullable=False),
        sa.Column('new_projects', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('existing_projects', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('new_submissions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('duplicate_submissions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('revisions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('invalid_rows', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=40), nullable=False, server_default='pending'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=160), nullable=False),
        sa.Column('created_by_role', sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("batch_id"),
    )
    op.create_index('ix_import_batches_status', 'import_batches', ['status'])
    op.create_index('ix_import_batches_started_at', 'import_batches', ['started_at'])
    
    # Create data_refresh_log table for tracking refresh operations
    op.create_table(
        'data_refresh_log',
        sa.Column('refresh_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('refresh_type', sa.String(length=80), nullable=False),
        sa.Column('triggered_by', sa.String(length=160), nullable=False),
        sa.Column('triggered_by_role', sa.String(length=80), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rows_processed', sa.Integer(), nullable=True),
        sa.Column('new_projects', sa.Integer(), nullable=True),
        sa.Column('new_submissions', sa.Integer(), nullable=True),
        sa.Column('revisions', sa.Integer(), nullable=True),
        sa.Column('invalid_rows', sa.Integer(), nullable=True),
        sa.Column('risk_records_refreshed', sa.Integer(), nullable=True),
        sa.Column('dcs_refreshed', sa.Boolean(), nullable=True),
        sa.Column('governance_changes', sa.Integer(), nullable=True),
        sa.Column('model_inferences_refreshed', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=40), nullable=False, server_default='in_progress'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("refresh_id"),
    )
    op.create_index('ix_data_refresh_log_refresh_type', 'data_refresh_log', ['refresh_type'])
    op.create_index('ix_data_refresh_log_start_time', 'data_refresh_log', ['start_time'])
    op.create_index('ix_data_refresh_log_status', 'data_refresh_log', ['status'])


def downgrade() -> None:
    op.drop_index('ix_data_refresh_log_status', table_name='data_refresh_log')
    op.drop_index('ix_data_refresh_log_start_time', table_name='data_refresh_log')
    op.drop_index('ix_data_refresh_log_refresh_type', table_name='data_refresh_log')
    op.drop_table('data_refresh_log')
    
    op.drop_index('ix_import_batches_started_at', table_name='import_batches')
    op.drop_index('ix_import_batches_status', table_name='import_batches')
    op.drop_table('import_batches')
    
    op.drop_index('ix_cuf_revisions_timestamp', table_name='cuf_revisions')
    op.drop_index('ix_cuf_revisions_submission_id', table_name='cuf_revisions')
    op.drop_table('cuf_revisions')
    
    op.drop_index('ix_cuf_submissions_is_latest', table_name='cuf_submissions')
    op.drop_constraint('fk_cuf_submissions_superseded_by', 'cuf_submissions')
    op.drop_column('cuf_submissions', 'provenance_status')
    op.drop_column('cuf_submissions', 'import_method')
    op.drop_column('cuf_submissions', 'source_date')
    op.drop_column('cuf_submissions', 'source_file')
    op.drop_column('cuf_submissions', 'data_source')
    op.drop_column('cuf_submissions', 'superseded_reason')
    op.drop_column('cuf_submissions', 'superseded_at')
    op.drop_column('cuf_submissions', 'superseded_by')
    op.drop_column('cuf_submissions', 'is_latest')
    op.drop_column('cuf_submissions', 'version')
    
    op.drop_index('ix_projects_project_code', table_name='projects')
    op.drop_column('projects', 'provenance_status')
    op.drop_column('projects', 'import_method')
    op.drop_column('projects', 'entered_by')
    op.drop_column('projects', 'source_date')
    op.drop_column('projects', 'source_file')
    op.drop_column('projects', 'data_source')
    op.drop_column('projects', 'revised_completion_date')
    op.drop_column('projects', 'original_completion_date')
    op.drop_column('projects', 'implementing_agency')
    op.drop_column('projects', 'department')
    op.drop_column('projects', 'project_code')
    op.drop_column('projects', 'project_name')
