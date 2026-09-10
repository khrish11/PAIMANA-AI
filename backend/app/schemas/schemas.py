"""Pydantic v2 response models for all Phase 2 API contracts."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────

class RiskCategory(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    CRITICAL = "CRITICAL"


class ConfidenceLabel(str, Enum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


class AnomalyType(str, Enum):
    EXPENDITURE_PROGRESS_MISMATCH = "expenditure_progress_mismatch"
    UNUSUALLY_FAST_PROGRESS = "unusually_fast_progress"
    SUDDEN_COST_ESCALATION = "sudden_cost_escalation"
    REPEATED_MILESTONE_SHIFT = "repeated_milestone_shift"


class AnomalySeverity(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class GovernanceActionType(str, Enum):
    INITIATE_REVIEW = "initiate_review"
    DEFER = "defer"
    OVERRIDE = "override"
    COMPLETE = "complete"


class NIDStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    PARTIAL = "partial"


class ContradictionSeverity(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    DELAYED = "delayed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"


class AuditActionType(str, Enum):
    CREATE_PROJECT = "create_project"
    UPDATE_PROJECT = "update_project"
    CUF_SUBMISSION = "cuf_submission"
    IMPORT = "import"
    RISK_RECALCULATION = "risk_recalculation"
    GOVERNANCE_ACTION = "governance_action"
    MODEL_PREDICTION = "model_prediction"
    SIMULATION = "simulation"
    REPORT_GENERATION = "report_generation"


# ─── Data Confidence Score ────────────────────────────────────────────────────

class DCSComponents(BaseModel):
    completeness: float = Field(..., ge=0, le=25, description="Score for data completeness (0-25)")
    freshness: float = Field(..., ge=0, le=25, description="Score for reporting freshness (0-25)")
    consistency: float = Field(..., ge=0, le=25, description="Score for internal consistency (0-25)")
    reliability: float = Field(..., ge=0, le=25, description="Score for agency reliability (0-25)")


class DCSResponse(BaseModel):
    dcs_score: float = Field(..., ge=0, le=100, description="Overall data confidence score (0-100)")
    components: DCSComponents
    confidence_label: ConfidenceLabel
    warning_flags: list[str] = Field(default_factory=list)


# ─── RCF / Probabilistic Forecasting ─────────────────────────────────────────

class RCFResponse(BaseModel):
    sector: str
    size_band: str
    region: str
    sample_count: int
    used_fallback: bool
    warning: str | None = None
    cost_overrun_p50: float
    cost_overrun_p80: float
    cost_overrun_p90: float
    schedule_delay_p50: float
    schedule_delay_p80: float
    schedule_delay_p90: float
    p50_final_cost: float
    p80_final_cost: float
    p90_final_cost: float
    p50_completion_months: float
    p80_completion_months: float
    p90_completion_months: float
    probability_overrun_gt_5: float
    probability_overrun_gt_10: float
    probability_overrun_gt_20: float
    reference_class: str


# ─── Anomaly Detection ───────────────────────────────────────────────────────

class AnomalyItem(BaseModel):
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    observed_value: float
    expected_value: float
    delta: float
    explanation: str
    reporting_period: str


class AnomalyResponse(BaseModel):
    project_id: str
    anomalies: list[AnomalyItem] = Field(default_factory=list)
    anomaly_count: int = 0


# ─── SHAP Explainability ─────────────────────────────────────────────────────

class SHAPDriver(BaseModel):
    feature_name: str
    human_label: str
    feature_value: float | str
    contribution: float
    direction: str = Field(..., description="'increases_risk' or 'decreases_risk'")
    explanation: str


class SHAPExplanation(BaseModel):
    drivers: list[SHAPDriver] = Field(default_factory=list, max_length=5)
    model_version: str = "rule_based_v1"
    method: str = "rule_based_fallback"
    status: str = "unavailable"
    model_type: str | None = None
    model_status: str | None = None
    predicted_probability: float | None = None
    predicted_class: int | None = None


# ─── Risk Scoring ────────────────────────────────────────────────────────────

class RiskComponentScores(BaseModel):
    cost_risk: float = Field(..., ge=0, le=100)
    schedule_risk: float = Field(..., ge=0, le=100)
    progress_anomaly_score: float = Field(..., ge=0, le=100)
    governance_risk: float = Field(..., ge=0, le=100)


class CalibrationMetadata(BaseModel):
    threshold_version: str = "v1_synthetic"
    weights: dict[str, float] = Field(default_factory=dict)
    thresholds: dict[str, float] = Field(default_factory=dict)
    note: str = "Thresholds calibrated on synthetic distribution; pending real PAIMANA/OCMS data."


class RiskResponse(BaseModel):
    project_id: str
    project_name: str
    ministry: str
    sector: str
    state: str
    status: str
    reporting_month: str
    composite_score: float = Field(..., ge=0, le=100)
    risk_category: RiskCategory
    components: RiskComponentScores
    dcs: DCSResponse
    shap: SHAPExplanation
    anomalies: list[AnomalyItem] = Field(default_factory=list)
    calibration: CalibrationMetadata = Field(default_factory=CalibrationMetadata)


# ─── NID ──────────────────────────────────────────────────────────────────────

class NIDContradiction(BaseModel):
    claim: str
    referenced_cuf_field: str
    expected_value: str
    actual_value: str
    coherence_score: float = Field(..., ge=0, le=1)
    severity: ContradictionSeverity
    explanation: str


class NIDResponse(BaseModel):
    project_id: str
    status: NIDStatus
    nqc_score: float | None = Field(None, ge=0, le=100)
    confidence: str | None = None
    extracted_claims: list[str] = Field(default_factory=list)
    contradictions: list[NIDContradiction] = Field(default_factory=list)
    model_version: str = "demo_rule_based_v1"
    prompt_version: str = "v1"
    error_message: str | None = None


# ─── PBE ──────────────────────────────────────────────────────────────────────

class PeerProject(BaseModel):
    anonymised_id: str
    cost_variance: float
    schedule_variance: float
    physical_progress: float
    risk_category: RiskCategory


class PBEResponse(BaseModel):
    project_id: str
    ppi_score: float = Field(..., ge=0, le=100)
    percentile: float = Field(..., ge=0, le=100)
    cohort_size: int
    cohort_sector: str
    cohort_size_band: str
    peer_relative_cost_variance: float
    peer_relative_schedule_variance: float
    peer_reporting_quality: float
    cohort_median_cost_overrun: float
    cohort_range_min: float
    cohort_range_max: float
    anonymised_peers: list[PeerProject] = Field(default_factory=list)
    explanation: str
    stage_normalised: bool = True


# ─── Governance ───────────────────────────────────────────────────────────────

class GovernanceQueueItem(BaseModel):
    project_id: str
    project_name: str
    risk_score: float
    risk_category: RiskCategory
    trigger_type: str
    dcs_score: float
    days_pending: int
    review_status: str
    triggered_at: str


class GovernanceActionRequest(BaseModel):
    project_id: str
    action_type: GovernanceActionType
    reviewer: str
    notes: str = ""


class GovernanceActionResponse(BaseModel):
    action_id: str
    project_id: str
    action_type: GovernanceActionType
    triggered_by: str
    reviewed_by: str
    outcome: str | None = None
    notes: str
    timestamp: str
    audit_confirmation: str


# ─── National Dashboard ──────────────────────────────────────────────────────

class KPIRow(BaseModel):
    total_projects: int
    high_risk_count: int
    very_high_critical_count: int
    avg_composite_risk: float
    avg_dcs: float
    projects_requiring_review: int


class SectorRisk(BaseModel):
    sector: str
    avg_risk: float
    project_count: int


class StateRisk(BaseModel):
    state: str
    project_count: int
    avg_risk: float
    high_risk_count: int
    avg_dcs: float


class AlertItem(BaseModel):
    alert_type: str
    severity: str
    message: str
    project_id: str | None = None
    timestamp: str


class TopRiskProject(BaseModel):
    project_id: str
    project_name: str
    ministry: str
    sector: str
    state: str
    risk_score: float
    risk_category: RiskCategory
    dcs_score: float
    top_driver: str


class NationalDashboardResponse(BaseModel):
    kpi: KPIRow
    sector_risks: list[SectorRisk]
    state_risks: list[StateRisk]
    top_risk_projects: list[TopRiskProject]
    alerts: list[AlertItem]
    data_source: str = "synthetic_demo"
    reporting_period: str


# ─── Projects ────────────────────────────────────────────────────────────────

class ProjectSummary(BaseModel):
    project_id: str
    project_name: str
    state: str
    sector: str
    ministry: str
    sanctioned_cost: float
    revised_cost: float | None = None
    physical_progress: float | None = None
    risk_score: float | None = None
    risk_category: RiskCategory | None = None
    dcs_score: float | None = None
    pbe_percentile: float | None = None
    nqc_score: float | None = None
    status: str
    last_updated: str


class ProjectListResponse(BaseModel):
    projects: list[ProjectSummary]
    total_count: int
    page: int = 1
    page_size: int = 50


# ─── Model Performance ──────────────────────────────────────────────────────

class ModelPerformanceEntry(BaseModel):
    model_type: str
    version: str
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    roc_auc: float | None = None
    pr_auc: float | None = None
    brier_score: float | None = None
    balanced_accuracy: float | None = None
    mcc: float | None = None
    trained_date: str
    is_active: bool
    sector_performance: dict[str, float] = Field(default_factory=dict)
    available: bool = True
    availability_reason: str | None = None
    target: str | None = None
    status: str = "EXPERIMENTAL"
    holdout_size: int | None = None
    training_period: str | None = None
    validation_period: str | None = None
    notes: str = ""


class ModelPerformanceResponse(BaseModel):
    models: list[ModelPerformanceEntry]
    active_model: str | None = None
    data_source: str = "synthetic_demo"
    holdout_size: int | None = None
    holdout_warning: str | None = None


# ─── Public Summary ──────────────────────────────────────────────────────────

class SectorOverrunStat(BaseModel):
    sector: str
    avg_cost_overrun_pct: float
    avg_schedule_delay_months: float
    project_count: int


class StateTrend(BaseModel):
    state: str
    avg_risk: float
    project_count: int


class PublicSummaryResponse(BaseModel):
    sector_overrun_stats: list[SectorOverrunStat]
    state_trends: list[StateTrend]
    total_projects: int
    overall_avg_risk: float
    overall_avg_cost_overrun_pct: float
    transparency_note: str = (
        "Aggregated statistics from PAIMANA-AI risk analytics. "
        "No project-level or agency-sensitive data is included."
    )
    data_source: str = "synthetic_demo"


# ─── Network / Blast-Radius (Scaffolded) ─────────────────────────────────────

class NetworkNode(BaseModel):
    id: str
    label: str
    node_type: str
    risk_category: RiskCategory | None = None
    value: float = 0


class NetworkEdge(BaseModel):
    source: str
    target: str
    relationship_type: str
    weight: float = 1.0


class NetworkResponse(BaseModel):
    nodes: list[NetworkNode] = Field(default_factory=list)
    edges: list[NetworkEdge] = Field(default_factory=list)
    available: bool = False
    message: str = "Network analysis backend not yet implemented (Phase 3/5)."
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContagionAlert(BaseModel):
    source_project_id: str
    affected_project_id: str
    relationship_type: str
    propagated_delta: float
    hop_distance: int
    timestamp: str


# ─── Simulation / Decision Cockpit (Scaffolded) ──────────────────────────────

class SimulationScenario(BaseModel):
    parameter: str
    current_value: float
    proposed_value: float


class SimulationRequest(BaseModel):
    project_id: str
    scenarios: list[SimulationScenario]


class SimulationResult(BaseModel):
    before_risk: float
    after_risk: float
    risk_delta: float
    before_cost: float
    after_cost: float
    cost_delta: float
    before_completion_months: float
    after_completion_months: float
    schedule_delta: float


class SimulationResponse(BaseModel):
    project_id: str
    results: SimulationResult | None = None
    available: bool = False
    message: str = "Decision Cockpit simulator not yet implemented (Phase 5)."
    audit_id: str | None = None


# ─── CUF Submission ──────────────────────────────────────────────────────────

class SubmissionCreate(BaseModel):
    project_id: str
    reporting_month: date
    revised_cost: float | None = None
    expenditure: float | None = None
    physical_progress: float | None = None
    planned_completion: date | None = None
    narrative_text: str | None = None
    submitted_by: str


class SubmissionResponse(BaseModel):
    submission_id: str
    project_id: str
    reporting_month: str
    status: str = "accepted"
    message: str = "Submission recorded successfully."
    version: int
    dcs_score: float | None = None
    risk_score: float | None = None
    anomaly_count: int = 0
    governance_status: str | None = None


# ─── Project Management ───────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=50)
    project_name: str = Field(..., min_length=1, max_length=200)
    ministry: str = Field(..., min_length=1, max_length=100)
    sector: str = Field(..., min_length=1, max_length=50)
    state: str = Field(..., min_length=1, max_length=50)
    implementing_agency: str = Field(..., min_length=1, max_length=100)
    sanctioned_cost: float = Field(..., gt=0)
    revised_cost: float | None = Field(None, gt=0)
    approval_date: date
    original_completion_date: date
    planned_completion_date: date | None = None
    actual_completion_date: date | None = None
    status: ProjectStatus = ProjectStatus.ONGOING
    reporting_month: date | None = None
    initial_expenditure: float | None = Field(None, ge=0)
    initial_physical_progress: float | None = Field(None, ge=0, le=100)
    initial_narrative: str | None = None


class ProjectUpdate(BaseModel):
    project_name: str | None = Field(None, min_length=1, max_length=200)
    ministry: str | None = Field(None, min_length=1, max_length=100)
    sector: str | None = Field(None, min_length=1, max_length=50)
    state: str | None = Field(None, min_length=1, max_length=50)
    implementing_agency: str | None = Field(None, min_length=1, max_length=100)
    sanctioned_cost: float | None = Field(None, gt=0)
    revised_cost: float | None = Field(None, gt=0)
    approval_date: date | None = None
    original_completion_date: date | None = None
    planned_completion_date: date | None = None
    actual_completion_date: date | None = None
    status: ProjectStatus | None = None
    reason_for_change: str = Field(..., min_length=10, max_length=500)


class ProjectResponse(BaseModel):
    project_id: str
    project_name: str
    ministry: str
    sector: str
    state: str
    implementing_agency: str
    sanctioned_cost: float
    revised_cost: float | None
    approval_date: date
    original_completion_date: date
    planned_completion_date: date | None
    actual_completion_date: date | None
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    version: int


class ProjectVersion(BaseModel):
    version: int
    project_id: str
    reporting_month: date | None
    changed_by: str
    changed_at: datetime
    changes: dict[str, tuple[str, str]]  # field: (old_value, new_value)
    reason: str


# ─── Data Health ───────────────────────────────────────────────────────────────

class DataHealthMetrics(BaseModel):
    total_records: int
    valid_records: int
    warning_records: int
    excluded_records: int
    duplicate_count: int
    unresolved_conflicts: int
    missing_critical_fields: int
    stale_projects: int
    low_dcs_projects: int
    anomaly_count: int
    latest_reporting_month: str | None


class DataHealthResponse(BaseModel):
    metrics: DataHealthMetrics
    data_quality_trend: list[dict[str, str | float]]
    missingness_by_field: dict[str, float]
    issues_by_month: dict[str, int]
    issues_by_sector: dict[str, int]
    issues_by_state: dict[str, int]


# ─── Audit Trail ───────────────────────────────────────────────────────────────

class AuditEvent(BaseModel):
    audit_id: str
    timestamp: datetime
    user: str
    role: str
    action: AuditActionType
    entity_type: str
    entity_id: str
    reason: str | None = None
    before_summary: dict[str, str] | None = None
    after_summary: dict[str, str] | None = None


class AuditResponse(BaseModel):
    events: list[AuditEvent]
    total_count: int
    page: int
    page_size: int


# ─── Import ───────────────────────────────────────────────────────────────────

class ImportPreview(BaseModel):
    total_rows: int
    valid_rows: int
    warning_rows: int
    rejected_rows: int
    duplicate_rows: int
    errors: list[dict[str, str | int]]
    warnings: list[dict[str, str | int]]


class ImportResult(BaseModel):
    import_id: str
    filename: str
    user: str
    timestamp: datetime
    successful_rows: int
    warning_rows: int
    rejected_rows: int
    preview: ImportPreview


# ─── Reports ─────────────────────────────────────────────────────────────────

class ReportMetadata(BaseModel):
    report_id: str
    report_type: str
    generated_by: str
    generated_at: datetime
    filters: dict[str, str | list[str]]
    reporting_period: str
    model_version: str | None = None
    data_snapshot_timestamp: datetime
    data_source: str = "real_paimana"


class NationalReportResponse(BaseModel):
    metadata: ReportMetadata
    total_projects: int
    risk_distribution: dict[str, int]
    high_risk_count: int
    very_high_count: int
    critical_count: int
    average_risk: float
    average_dcs: float
    state_level_risk: dict[str, dict[str, float | int]]
    sector_level_risk: dict[str, dict[str, float | int]]
    anomaly_count: int
    governance_queue_stats: dict[str, int]
    model_status: str


class ProjectReportResponse(BaseModel):
    metadata: ReportMetadata
    project_profile: dict[str, str | float | date]
    risk: dict[str, float | str]
    ml: dict[str, str | float | bool] | None
    rcf: dict[str, str | float | bool] | None
    anomalies: list[dict[str, str | float]]
    nid: dict[str, str | float] | None
    pbe: dict[str, str | float] | None
    governance: dict[str, str | list[dict]]
    trend: list[dict[str, str | float]]


class SectorStateReportResponse(BaseModel):
    metadata: ReportMetadata
    sector_or_state: str
    project_count: int
    average_risk: float
    risk_distribution: dict[str, int]
    average_dcs: float
    anomalies: int
    high_risk_projects: list[dict[str, str | float]]
    trend: list[dict[str, str | float]]


class GovernanceReportResponse(BaseModel):
    metadata: ReportMetadata
    total_reviews: int
    open_reviews: int
    completed_reviews: int
    overdue_reviews: int
    high_risk_count: int
    very_high_count: int
    critical_count: int
    review_sla: dict[str, float]
    actions_taken: list[dict[str, str]]
    outcomes: dict[str, int]


class ModelReportResponse(BaseModel):
    metadata: ReportMetadata
    models: list[dict[str, str | float]]
    training_period: str
    holdout_size: int
    experimental_warning: str
    shap_available: bool


class ReportHistoryResponse(BaseModel):
    reports: list[ReportMetadata]
    total_count: int
    page: int
    page_size: int


# ─── Risk Trend ───────────────────────────────────────────────────────────────

class RiskTrendPoint(BaseModel):
    reporting_month: str
    composite_score: float
    cost_risk: float
    schedule_risk: float
    dcs_score: float
    anomaly_score: float


class RiskTrendResponse(BaseModel):
    project_id: str
    trend: list[RiskTrendPoint] = Field(default_factory=list)


# ─── Positive Deviance Radar ────────────────────────────────────────────────────

class PositiveDeviantResponse(BaseModel):
    deviant_id: str
    project_id: str
    project_name: str | None = None
    sector: str | None = None
    state: str | None = None
    reference_class_id: str | None = None
    reporting_month: date
    residual_cost_zscore: float
    residual_schedule_zscore: float
    data_confidence_score: float
    months_active: int
    deviance_method: str
    threshold_used: float
    detected_at: datetime


class PositiveDeviantsListResponse(BaseModel):
    positive_deviants: list[PositiveDeviantResponse] = Field(default_factory=list)
    total_count: int
    metadata: dict[str, int] = Field(default_factory=dict)


class ExtractedActionResponse(BaseModel):
    action_id: str
    deviant_id: str
    project_id: str
    action_text: str
    category: str
    source_month: str
    quote_evidence: str | None = None
    specificity_score: int
    llm_model_version: str | None = None
    prompt_version: str | None = None
    extracted_at: datetime


class PlaybookResponse(BaseModel):
    playbook_id: str
    category: str
    label: str
    confidence_tier: str
    source_project_count: int
    source_action_ids: list[str] = Field(default_factory=list)
    evidence_actions: list[ExtractedActionResponse] = Field(default_factory=list)
    created_at: datetime
    last_updated_at: datetime


class PlaybooksListResponse(BaseModel):
    playbooks: list[PlaybookResponse] = Field(default_factory=list)
    total_count: int
    filters_applied: dict[str, str] = Field(default_factory=dict)


class PlaybookSuggestionResponse(BaseModel):
    suggestion_id: str
    project_id: str
    playbook: PlaybookResponse
    triggered_by_risk_category: str | None = None
    suggested_at: datetime
    was_viewed: bool
    was_dismissed: bool
    relevance_score: float | None = None
    trigger_reason: str | None = None


class PlaybookSuggestionsResponse(BaseModel):
    suggestions: list[PlaybookSuggestionResponse] = Field(default_factory=list)
    project_id: str
    total_count: int


# ─── Continuous Data Operations ────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    project_name: str | None = None
    project_code: str | None = None
    sector: str
    ministry: str
    department: str | None = None
    state: str
    implementing_agency: str | None = None
    sanctioned_cost: float
    approved_date: date
    original_completion_date: date | None = None
    revised_completion_date: date | None = None
    status: str = "ONGOING"
    data_source: str | None = None
    source_file: str | None = None
    source_date: date | None = None
    import_method: str | None = None
    provenance_status: str | None = None


class ProjectResponse(BaseModel):
    project_id: str
    project_name: str | None = None
    project_code: str | None = None
    sector: str
    ministry: str
    department: str | None = None
    state: str
    implementing_agency: str | None = None
    sanctioned_cost: float
    approved_date: str | None = None
    original_completion_date: str | None = None
    revised_completion_date: str | None = None
    status: str
    created_at: str | None = None
    updated_at: str | None = None


class SubmissionCreate(BaseModel):
    reporting_month: date
    project_id: str | None = None
    submitted_by: str | None = None
    revised_cost: float | None = None
    expenditure: float | None = None
    physical_progress: float | None = None
    planned_completion: date | None = None
    narrative_text: str | None = None
    revision_reason: str | None = None
    data_source: str | None = None
    source_file: str | None = None
    source_date: date | None = None
    import_method: str | None = None
    provenance_status: str | None = None


class SubmissionResponse(BaseModel):
    submission_id: str
    project_id: str
    reporting_month: str | None = None
    status: str
    message: str
    version: int
    dcs_score: float | None = None
    risk_score: float | None = None
    anomaly_count: int | None = None
    governance_status: str | None = None
