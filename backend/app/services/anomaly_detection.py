"""Deterministic, explainable anomaly detection service.

Implements four anomaly rules from the SRS:
A. Expenditure significantly outpacing physical progress
B. Unusually fast reported progress relative to RCF trajectory
C. Sudden cost escalation relative to project history
D. Repeated milestone-date movement across consecutive periods
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AnomalyType(str, Enum):
    EXPENDITURE_PROGRESS_MISMATCH = "expenditure_progress_mismatch"
    UNUSUALLY_FAST_PROGRESS = "unusually_fast_progress"
    SUDDEN_COST_ESCALATION = "sudden_cost_escalation"
    REPEATED_MILESTONE_SHIFT = "repeated_milestone_shift"


class Severity(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class AnomalyResult:
    anomaly_type: AnomalyType
    severity: Severity
    observed_value: float
    expected_value: float
    delta: float
    explanation: str
    reporting_period: str


# ─── Thresholds (configurable; defaults calibrated on synthetic distribution) ─

# Rule A: expenditure-to-progress gap thresholds
EXPENDITURE_GAP_MODERATE = 0.15
EXPENDITURE_GAP_HIGH = 0.25
EXPENDITURE_GAP_CRITICAL = 0.40

# Rule B: progress velocity relative to RCF median monthly rate
PROGRESS_VELOCITY_FAST_MODERATE = 1.8  # 80% faster than expected
PROGRESS_VELOCITY_FAST_HIGH = 2.5

# Rule C: month-over-month cost escalation thresholds
COST_ESCALATION_MODERATE = 0.05  # 5% in one month
COST_ESCALATION_HIGH = 0.10
COST_ESCALATION_CRITICAL = 0.20

# Rule D: milestone shift count thresholds
MILESTONE_SHIFT_MODERATE = 2
MILESTONE_SHIFT_HIGH = 3
MILESTONE_SHIFT_CRITICAL = 5


def _severity_from_gap(gap: float, moderate: float, high: float, critical: float) -> Severity:
    if abs(gap) >= critical:
        return Severity.CRITICAL
    if abs(gap) >= high:
        return Severity.HIGH
    if abs(gap) >= moderate:
        return Severity.MODERATE
    return Severity.LOW


def detect_expenditure_progress_mismatch(
    *,
    expenditure_ratio: float,
    physical_progress_pct: float,
    reporting_period: str,
) -> AnomalyResult | None:
    """Rule A: expenditure significantly outpacing physical progress."""
    progress_ratio = physical_progress_pct / 100.0
    gap = expenditure_ratio - progress_ratio

    if gap < EXPENDITURE_GAP_MODERATE:
        return None

    severity = _severity_from_gap(gap, EXPENDITURE_GAP_MODERATE, EXPENDITURE_GAP_HIGH, EXPENDITURE_GAP_CRITICAL)

    return AnomalyResult(
        anomaly_type=AnomalyType.EXPENDITURE_PROGRESS_MISMATCH,
        severity=severity,
        observed_value=round(expenditure_ratio, 4),
        expected_value=round(progress_ratio, 4),
        delta=round(gap, 4),
        explanation=(
            f"Expenditure ratio ({expenditure_ratio:.1%}) exceeds physical progress "
            f"({physical_progress_pct:.1f}%) by {gap:.1%}. "
            f"This may indicate cost overruns without corresponding physical work, "
            f"inflated expenditure claims, or procurement-heavy phases."
        ),
        reporting_period=reporting_period,
    )


def detect_unusually_fast_progress(
    *,
    monthly_progress_rate: float,
    rcf_median_monthly_rate: float,
    reporting_period: str,
) -> AnomalyResult | None:
    """Rule B: unusually fast reported progress relative to reference-class trajectory."""
    if rcf_median_monthly_rate <= 0:
        return None

    ratio = monthly_progress_rate / rcf_median_monthly_rate

    if ratio < PROGRESS_VELOCITY_FAST_MODERATE:
        return None

    severity = Severity.HIGH if ratio >= PROGRESS_VELOCITY_FAST_HIGH else Severity.MODERATE

    return AnomalyResult(
        anomaly_type=AnomalyType.UNUSUALLY_FAST_PROGRESS,
        severity=severity,
        observed_value=round(monthly_progress_rate, 4),
        expected_value=round(rcf_median_monthly_rate, 4),
        delta=round(monthly_progress_rate - rcf_median_monthly_rate, 4),
        explanation=(
            f"Reported monthly progress rate ({monthly_progress_rate:.1f}% per month) is "
            f"{ratio:.1f}x the reference-class median ({rcf_median_monthly_rate:.1f}% per month). "
            f"This may indicate inflated progress reporting or a genuinely accelerated phase."
        ),
        reporting_period=reporting_period,
    )


def detect_sudden_cost_escalation(
    *,
    current_revised_cost: float,
    previous_revised_cost: float,
    reporting_period: str,
) -> AnomalyResult | None:
    """Rule C: sudden cost escalation relative to project history."""
    if previous_revised_cost <= 0:
        return None

    escalation = (current_revised_cost - previous_revised_cost) / previous_revised_cost

    if escalation < COST_ESCALATION_MODERATE:
        return None

    severity = _severity_from_gap(
        escalation, COST_ESCALATION_MODERATE, COST_ESCALATION_HIGH, COST_ESCALATION_CRITICAL
    )

    return AnomalyResult(
        anomaly_type=AnomalyType.SUDDEN_COST_ESCALATION,
        severity=severity,
        observed_value=round(current_revised_cost, 2),
        expected_value=round(previous_revised_cost, 2),
        delta=round(current_revised_cost - previous_revised_cost, 2),
        explanation=(
            f"Revised cost increased by {escalation:.1%} in a single reporting period "
            f"(from ₹{previous_revised_cost:.2f} Cr to ₹{current_revised_cost:.2f} Cr). "
            f"Sudden cost jumps may indicate scope changes, underestimation, or contract amendments."
        ),
        reporting_period=reporting_period,
    )


def detect_repeated_milestone_shift(
    *,
    milestone_shift_count: int,
    total_shift_months: float,
    reporting_period: str,
) -> AnomalyResult | None:
    """Rule D: repeated milestone-date movement across consecutive periods."""
    if milestone_shift_count < MILESTONE_SHIFT_MODERATE:
        return None

    severity = _severity_from_gap(
        milestone_shift_count,
        MILESTONE_SHIFT_MODERATE,
        MILESTONE_SHIFT_HIGH,
        MILESTONE_SHIFT_CRITICAL,
    )

    return AnomalyResult(
        anomaly_type=AnomalyType.REPEATED_MILESTONE_SHIFT,
        severity=severity,
        observed_value=float(milestone_shift_count),
        expected_value=0.0,
        delta=float(milestone_shift_count),
        explanation=(
            f"Planned completion date has shifted {milestone_shift_count} times across "
            f"reporting periods, with a total delay of {total_shift_months:.0f} months. "
            f"Frequent milestone revisions suggest planning instability or persistent blockers."
        ),
        reporting_period=reporting_period,
    )


def detect_all_anomalies(
    *,
    expenditure_ratio: float | None = None,
    physical_progress_pct: float | None = None,
    monthly_progress_rate: float | None = None,
    rcf_median_monthly_rate: float | None = None,
    current_revised_cost: float | None = None,
    previous_revised_cost: float | None = None,
    milestone_shift_count: int = 0,
    total_shift_months: float = 0,
    reporting_period: str = "",
) -> list[AnomalyResult]:
    """Run all four anomaly detection rules and return flagged anomalies."""
    anomalies: list[AnomalyResult] = []

    if expenditure_ratio is not None and physical_progress_pct is not None:
        result = detect_expenditure_progress_mismatch(
            expenditure_ratio=expenditure_ratio,
            physical_progress_pct=physical_progress_pct,
            reporting_period=reporting_period,
        )
        if result is not None:
            anomalies.append(result)

    if monthly_progress_rate is not None and rcf_median_monthly_rate is not None:
        result = detect_unusually_fast_progress(
            monthly_progress_rate=monthly_progress_rate,
            rcf_median_monthly_rate=rcf_median_monthly_rate,
            reporting_period=reporting_period,
        )
        if result is not None:
            anomalies.append(result)

    if current_revised_cost is not None and previous_revised_cost is not None:
        result = detect_sudden_cost_escalation(
            current_revised_cost=current_revised_cost,
            previous_revised_cost=previous_revised_cost,
            reporting_period=reporting_period,
        )
        if result is not None:
            anomalies.append(result)

    if milestone_shift_count >= MILESTONE_SHIFT_MODERATE:
        result = detect_repeated_milestone_shift(
            milestone_shift_count=milestone_shift_count,
            total_shift_months=total_shift_months,
            reporting_period=reporting_period,
        )
        if result is not None:
            anomalies.append(result)

    return anomalies
