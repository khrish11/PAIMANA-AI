"""Positive Deviance Detector service.

Identifies projects performing significantly better than comparable projects
by calculating residuals against reference class statistics and applying
DCS guardrails and minimum track record requirements.

Configurable thresholds:
- MIN_TRACK_RECORD: minimum months of data required
- MIN_DCS: minimum data confidence score
- DEVIANCE_THRESHOLD: z-score or percentile threshold
- THRESHOLD_METHOD: 'zscore' or 'percentile'
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

import numpy as np
import pandas as pd

from app.services.rcf_engine import RCFResult, fit_reference_class
from app.services.risk_scoring import RiskScoreResult
from app.db.session import SessionLocal
from app.models.projects import Project
from app.models.cuf_submissions import CUFSubmission
from app.models.risk_scores import RiskScore

logger = logging.getLogger(__name__)

# Configurable thresholds
MIN_TRACK_RECORD = 6  # minimum months of data required
MIN_DCS = 70  # minimum data confidence score
DEVIANCE_THRESHOLD = -1.5  # negative z-score (better than reference)
THRESHOLD_METHOD: Literal["zscore", "percentile"] = "zscore"


@dataclass(frozen=True)
class PositiveDeviantResult:
    project_id: str
    reference_class_id: str | None
    reporting_month: date
    residual_cost_zscore: float
    residual_schedule_zscore: float
    data_confidence_score: float
    months_active: int
    deviance_method: str
    threshold_used: float


def calculate_residuals(
    project_cost_overrun: float,
    project_schedule_slip: float,
    reference_class: RCFResult | None,
) -> tuple[float, float]:
    """Calculate cost and schedule residuals against reference class.
    
    Args:
        project_cost_overrun: Project's cost overrun ratio
        project_schedule_slip: Project's schedule slip in months
        reference_class: Reference class statistics from RCF
    
    Returns:
        Tuple of (residual_cost, residual_schedule)
    """
    if reference_class is None:
        return 0.0, 0.0
    
    residual_cost = project_cost_overrun - float(reference_class.cost_overrun_p50)
    residual_schedule = project_schedule_slip - float(reference_class.schedule_delay_p50)
    
    return residual_cost, residual_schedule


def calculate_zscore(
    value: float,
    mean: float,
    std: float,
) -> float:
    """Calculate z-score for a value given distribution statistics.
    
    Args:
        value: The value to calculate z-score for
        mean: Mean of the distribution
        std: Standard deviation of the distribution
    
    Returns:
        Z-score (negative means better than average for cost/schedule)
    """
    if std == 0:
        return 0.0
    return (value - mean) / std


def get_reference_class_statistics(
    sector: str,
    state: str,
    sanctioned_cost: float,
) -> tuple[RCFResult | None, str | None]:
    """Get reference class statistics for a project.
    
    Args:
        sector: Project sector
        state: Project state
        sanctioned_cost: Project sanctioned cost
    
    Returns:
        Tuple of (RCFResult, class_id)
    """
    try:
        # Get size band
        if sanctioned_cost < 500:
            size_band = "150-500 Cr"
        elif sanctioned_cost < 2000:
            size_band = "500-2000 Cr"
        else:
            size_band = "2000+ Cr"
        
        # Fit reference class
        rcf_result = fit_reference_class(
            sector=sector,
            state=state,
            size_band=size_band,
            min_cluster_size=15,
        )
        
        # Generate class_id (in production, this would come from database)
        class_id = f"{sector}_{size_band}_{state}".replace(" ", "_").lower()
        
        return rcf_result, class_id
    except Exception as exc:
        logger.error("Failed to get reference class statistics: %s", exc)
        return None, None


def detect_positive_deviant(
    project_id: str,
    sector: str,
    state: str,
    sanctioned_cost: float,
    cost_overrun_ratio: float,
    schedule_slip_months: float,
    data_confidence_score: float,
    months_active: int,
    reporting_month: date,
) -> PositiveDeviantResult | None:
    """Detect if a project is a positive deviant.
    
    A project is a positive deviant when:
    1. Reference class is sufficiently difficult (sample size >= 15)
    2. Performance is materially better than class (negative residual)
    3. Has at least MIN_TRACK_RECORD months
    4. DCS >= MIN_DCS
    
    Args:
        project_id: Project identifier
        sector: Project sector
        state: Project state
        sanctioned_cost: Project sanctioned cost
        cost_overrun_ratio: Project cost overrun ratio
        schedule_slip_months: Project schedule slip in months
        data_confidence_score: Data confidence score (DCS)
        months_active: Number of months project has been active
        reporting_month: Reporting month for this detection
    
    Returns:
        PositiveDeviantResult if project is a positive deviant, None otherwise
    """
    # Guardrail: minimum track record
    if months_active < MIN_TRACK_RECORD:
        logger.debug(
            "Project %s not a positive deviant: insufficient track record (%d < %d)",
            project_id, months_active, MIN_TRACK_RECORD
        )
        return None
    
    # Guardrail: minimum DCS
    if data_confidence_score < MIN_DCS:
        logger.debug(
            "Project %s not a positive deviant: insufficient DCS (%.1f < %d)",
            project_id, data_confidence_score, MIN_DCS
        )
        return None
    
    # Get reference class statistics
    rcf_result, class_id = get_reference_class_statistics(sector, state, sanctioned_cost)
    
    if rcf_result is None or rcf_result.sample_count < 15:
        logger.debug(
            "Project %s not a positive deviant: insufficient reference class sample size",
            project_id
        )
        return None
    
    # Calculate residuals
    residual_cost, residual_schedule = calculate_residuals(
        cost_overrun_ratio, schedule_slip_months, rcf_result
    )
    
    # Calculate z-scores (need distribution from reference class)
    # For now, use a simplified approach with the residual directly
    # In production, would need full distribution statistics
    residual_cost_zscore = residual_cost / (float(rcf_result.cost_overrun_p80) - float(rcf_result.cost_overrun_p50)) if rcf_result.cost_overrun_p80 and rcf_result.cost_overrun_p50 else 0.0
    residual_schedule_zscore = residual_schedule / 10.0  # Simplified: 10 months as std dev
    
    # Check if performance is materially better (negative residual)
    if residual_cost_zscore > DEVIANCE_THRESHOLD and residual_schedule_zscore > DEVIANCE_THRESHOLD:
        logger.debug(
            "Project %s not a positive deviant: performance not materially better than class",
            project_id
        )
        return None
    
    # Project is a positive deviant
    return PositiveDeviantResult(
        project_id=project_id,
        reference_class_id=class_id,
        reporting_month=reporting_month,
        residual_cost_zscore=residual_cost_zscore,
        residual_schedule_zscore=residual_schedule_zscore,
        data_confidence_score=data_confidence_score,
        months_active=months_active,
        deviance_method=THRESHOLD_METHOD,
        threshold_used=DEVIANCE_THRESHOLD,
    )


def batch_detect_positive_deviants(
    projects_df: pd.DataFrame,
    reporting_month: date,
) -> list[PositiveDeviantResult]:
    """Detect positive deviants across all projects for a given month.
    
    Args:
        projects_df: DataFrame with project data
        reporting_month: Reporting month to detect for
    
    Returns:
        List of PositiveDeviantResult objects
    """
    positive_deviants = []
    
    for _, row in projects_df.iterrows():
        try:
            result = detect_positive_deviant(
                project_id=str(row.get("project_id", "")),
                sector=row.get("sector", ""),
                state=row.get("state", ""),
                sanctioned_cost=float(row.get("sanctioned_cost", 0)),
                cost_overrun_ratio=float(row.get("cost_overrun_ratio", 0)),
                schedule_slip_months=float(row.get("schedule_slip_months", 0)),
                data_confidence_score=float(row.get("dcs_score", 0)),
                months_active=int(row.get("months_active", 0)),
                reporting_month=reporting_month,
            )
            
            if result:
                positive_deviants.append(result)
        except Exception as exc:
            logger.error("Failed to detect positive deviant for project %s: %s", row.get("project_id"), exc)
    
    logger.info("Detected %d positive deviants for month %s", len(positive_deviants), reporting_month)
    return positive_deviants


class PositiveDevianceDetector:
    """Compatibility wrapper for positive deviance detection logic."""

    def __init__(self):
        self.min_track_record = MIN_TRACK_RECORD
        self.min_dcs = MIN_DCS
        self.deviance_threshold = DEVIANCE_THRESHOLD

    @staticmethod
    def _calculate_cost_residual(current_cost: float, sanctioned_cost: float, reference_cost_overrun: float) -> float:
        current_ratio = current_cost / sanctioned_cost if sanctioned_cost else 1.0
        return (current_ratio - 1.0) - float(reference_cost_overrun)

    @staticmethod
    def _calculate_schedule_residual(elapsed_months: float, planned_duration_months: float, progress_percent: float, reference_schedule_delay: float) -> float:
        adjusted_progress = elapsed_months - (0.5 * planned_duration_months)
        return adjusted_progress - float(reference_schedule_delay)

    @staticmethod
    def _residual_to_zscore(residual: float, std: float) -> float:
        if std == 0:
            return 0.0
        return residual / float(std)

    @staticmethod
    def _is_positive_deviant(project: dict, reference_class: dict) -> bool:
        months_tracked = int(project.get("months_tracked", 0))
        if months_tracked < MIN_TRACK_RECORD:
            return False

        data_confidence_score = float(project.get("data_confidence_score", 0))
        if data_confidence_score < MIN_DCS:
            return False

        sample_count = int(reference_class.get("sample_count", 0))
        if sample_count < 15:
            return False

        current_cost = float(project.get("current_cost", project.get("sanctioned_cost", 0)))
        sanctioned_cost = float(project.get("sanctioned_cost", 0))
        reference_cost_overrun = float(reference_class.get("cost_overrun_p50", 0))
        reference_schedule_delay = float(reference_class.get("schedule_delay_p50", 0))

        cost_residual = PositiveDevianceDetector._calculate_cost_residual(
            current_cost, sanctioned_cost, reference_cost_overrun
        )
        schedule_residual = PositiveDevianceDetector._calculate_schedule_residual(
            float(project.get("elapsed_months", 0)),
            float(project.get("planned_duration_months", 0)),
            float(project.get("progress_percent", 0)),
            reference_schedule_delay,
        )

        if cost_residual >= 0 and schedule_residual >= 0:
            return False

        return True

    def batch_detect(self, db=None, limit: int = 100, offset: int = 0, sector: str = None, state: str = None):
        """Detect positive deviants with filtering options.
        
        Args:
            db: Database session (optional, will create one if not provided)
            limit: Maximum number of results to return
            offset: Number of results to skip
            sector: Filter by sector
            state: Filter by state
        
        Returns:
            Dictionary with positive_deviants list and metadata
        """
        session = db or SessionLocal()
        
        try:
            # Query projects with their latest submissions and risk scores
            query = session.query(
                Project.project_id,
                Project.sector,
                Project.state,
                Project.sanctioned_cost,
                CUFSubmission.expenditure,
                CUFSubmission.physical_progress,
                CUFSubmission.reporting_month,
                RiskScore.data_confidence_score,
                RiskScore.composite_score
            ).join(
                CUFSubmission, Project.project_id == CUFSubmission.project_id
            ).join(
                RiskScore, Project.project_id == RiskScore.project_id
            ).filter(
                RiskScore.reporting_month == CUFSubmission.reporting_month
            )
            
            # Apply filters
            if sector:
                query = query.filter(Project.sector == sector)
            if state:
                query = query.filter(Project.state == state)
            
            # Get all matching projects
            projects = query.all()
            
            positive_deviants = []
            
            for proj in projects:
                try:
                    # Calculate months active (count submissions)
                    months_active = session.query(CUFSubmission).filter(
                        CUFSubmission.project_id == proj.project_id
                    ).count()
                    
                    # Calculate cost overrun ratio
                    cost_overrun_ratio = 0.0
                    if proj.sanctioned_cost and proj.sanctioned_cost > 0 and proj.expenditure:
                        cost_overrun_ratio = (float(proj.expenditure) - float(proj.sanctioned_cost)) / float(proj.sanctioned_cost)
                    
                    # Calculate schedule slip (simplified)
                    schedule_slip_months = 0.0  # Would need planned completion date
                    
                    # Get DCS score safely
                    dcs_score = float(proj.data_confidence_score) if proj.data_confidence_score else 0.0
                    
                    # Detect positive deviant
                    result = detect_positive_deviant(
                        project_id=str(proj.project_id),
                        sector=proj.sector or "",
                        state=proj.state or "",
                        sanctioned_cost=float(proj.sanctioned_cost),
                        cost_overrun_ratio=cost_overrun_ratio,
                        schedule_slip_months=schedule_slip_months,
                        data_confidence_score=dcs_score,
                        months_active=months_active,
                        reporting_month=proj.reporting_month or date.today()
                    )
                    
                    if result:
                        positive_deviants.append({
                            "project_id": result.project_id,
                            "reference_class_id": result.reference_class_id,
                            "reporting_month": result.reporting_month.isoformat(),
                            "residual_cost_zscore": result.residual_cost_zscore,
                            "residual_schedule_zscore": result.residual_schedule_zscore,
                            "data_confidence_score": result.data_confidence_score,
                            "months_active": result.months_active,
                            "deviance_method": result.deviance_method,
                            "threshold_used": result.threshold_used
                        })
                except Exception as exc:
                    logger.error("Failed to process project %s: %s", proj.project_id, exc)
            
            # Apply pagination
            total_count = len(positive_deviants)
            paginated_results = positive_deviants[offset:offset + limit]
            
            return {
                "positive_deviants": paginated_results,
                "metadata": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "data_source": "REAL_PAIMANA"
                }
            }
            
        except Exception as exc:
            logger.error("Failed to detect positive deviants: %s", exc)
            return {
                "positive_deviants": [],
                "metadata": {
                    "total_count": 0,
                    "error": str(exc),
                    "data_source": "REAL_PAIMANA"
                }
            }
        finally:
            if db is None:
                session.close()
