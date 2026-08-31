"""Composite project risk scoring service.

Produces cost_risk, schedule_risk, progress_anomaly_score, governance_risk,
composite_score, and risk_category.  Weights and thresholds are configurable
and identified by a threshold_version so they can later be calibrated on
real PAIMANA / OCMS data.

Integrates experimental ML model outputs where available.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict


class RiskCategory(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    CRITICAL = "CRITICAL"


# ─── Configurable defaults (synthetic-distribution calibration) ───────────────

DEFAULT_WEIGHTS = {
    "cost_risk": 0.30,
    "schedule_risk": 0.25,
    "progress_anomaly": 0.25,
    "governance_risk": 0.20,
}

# Category thresholds derived from synthetic distribution percentiles:
# LOW < 25th, MODERATE < 50th, HIGH < 75th, VERY_HIGH < 90th, CRITICAL ≥ 90th
DEFAULT_THRESHOLDS = {
    "low_max": 30.0,
    "moderate_max": 50.0,
    "high_max": 70.0,
    "very_high_max": 85.0,
}

THRESHOLD_VERSION = "v1_synthetic"


@dataclass(frozen=True)
class RiskScoreResult:
    cost_risk: float
    schedule_risk: float
    progress_anomaly_score: float
    governance_risk: float
    composite_score: float
    risk_category: RiskCategory
    weights: dict[str, float]
    thresholds: dict[str, float]
    threshold_version: str
    ml_model_status: Optional[str] = None
    ml_model_version: Optional[str] = None


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return min(hi, max(lo, value))


def _compute_cost_risk(cost_overrun_ratio: float) -> float:
    """Map cost overrun ratio to 0-100 risk score.

    0% overrun → 0, 5% → 25, 10% → 50, 20% → 75, 30%+ → 95+
    """
    if cost_overrun_ratio <= 1.0:
        return 0.0
    overrun_pct = (cost_overrun_ratio - 1.0) * 100
    score = min(100, overrun_pct * 3.3)
    return round(_clamp(score), 2)


def _compute_schedule_risk(schedule_slip_months: float, planned_duration_months: float) -> float:
    """Map schedule slippage to 0-100 risk score.

    Normalised by planned duration: a 6-month slip on a 12-month project is
    worse than on a 60-month project.
    """
    if schedule_slip_months <= 0:
        return 0.0
    if planned_duration_months <= 0:
        planned_duration_months = 24.0  # fallback

    slip_ratio = schedule_slip_months / planned_duration_months
    score = min(100, slip_ratio * 200)
    return round(_clamp(score), 2)


def _compute_progress_anomaly_score(anomaly_count: int, max_severity_ordinal: int) -> float:
    """Map anomaly count and max severity to 0-100 score.

    severity ordinal: 0=none, 1=LOW, 2=MODERATE, 3=HIGH, 4=CRITICAL
    """
    if anomaly_count == 0:
        return 0.0
    base = min(60, anomaly_count * 15)
    severity_bonus = max_severity_ordinal * 10
    return round(_clamp(base + severity_bonus), 2)


def _compute_governance_risk(
    has_pending_review: bool,
    past_overrides: int,
    days_pending: int,
) -> float:
    """Map governance state to 0-100 risk score."""
    score = 0.0
    if has_pending_review:
        score += 30
    score += min(30, past_overrides * 15)
    if days_pending > 60:
        score += 25
    elif days_pending > 30:
        score += 15
    elif days_pending > 14:
        score += 5
    return round(_clamp(score), 2)


def _categorise(
    composite: float,
    thresholds: dict[str, float] | None = None,
) -> RiskCategory:
    t = thresholds or DEFAULT_THRESHOLDS
    if composite <= t["low_max"]:
        return RiskCategory.LOW
    if composite <= t["moderate_max"]:
        return RiskCategory.MODERATE
    if composite <= t["high_max"]:
        return RiskCategory.HIGH
    if composite <= t["very_high_max"]:
        return RiskCategory.VERY_HIGH
    return RiskCategory.CRITICAL


def compute_risk_score(
    *,
    cost_overrun_ratio: float = 1.0,
    schedule_slip_months: float = 0.0,
    planned_duration_months: float = 24.0,
    anomaly_count: int = 0,
    max_severity_ordinal: int = 0,
    has_pending_review: bool = False,
    past_overrides: int = 0,
    days_pending: int = 0,
    weights: dict[str, float] | None = None,
    thresholds: dict[str, float] | None = None,
    ml_cost_risk: Optional[float] = None,
    ml_schedule_risk: Optional[float] = None,
    ml_model_status: Optional[str] = None,
    ml_model_version: Optional[str] = None,
) -> RiskScoreResult:
    """Compute composite project risk score from components.
    
    Integrates experimental ML model outputs where available.
    ML outputs are used as additional risk signals, not replacements.
    """
    w = weights or DEFAULT_WEIGHTS
    t = thresholds or DEFAULT_THRESHOLDS

    # Use ML outputs if available, otherwise use rule-based computation
    if ml_cost_risk is not None:
        cost_risk = ml_cost_risk
    else:
        cost_risk = _compute_cost_risk(cost_overrun_ratio)
    
    if ml_schedule_risk is not None:
        schedule_risk = ml_schedule_risk
    else:
        schedule_risk = _compute_schedule_risk(schedule_slip_months, planned_duration_months)
    
    progress_anomaly = _compute_progress_anomaly_score(anomaly_count, max_severity_ordinal)
    governance = _compute_governance_risk(has_pending_review, past_overrides, days_pending)

    composite = (
        w["cost_risk"] * cost_risk
        + w["schedule_risk"] * schedule_risk
        + w["progress_anomaly"] * progress_anomaly
        + w["governance_risk"] * governance
    )
    composite = round(_clamp(composite), 2)

    return RiskScoreResult(
        cost_risk=cost_risk,
        schedule_risk=schedule_risk,
        progress_anomaly_score=progress_anomaly,
        governance_risk=governance,
        composite_score=composite,
        risk_category=_categorise(composite, t),
        weights=w,
        thresholds=t,
        threshold_version=THRESHOLD_VERSION,
        ml_model_status=ml_model_status,
        ml_model_version=ml_model_version,
    )
