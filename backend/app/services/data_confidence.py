"""Data Confidence Score (DCS) service.

Computes a deterministic 0-100 confidence score from four components:
completeness, freshness, internal consistency, and agency reliability.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DCSResult:
    dcs_score: float
    completeness: float
    freshness: float
    consistency: float
    reliability: float
    confidence_label: str
    warning_flags: list[str]


# ─── Component Weights (each 0-25, total 0-100) ────────────────────────────

MAX_COMPONENT = 25.0


def _completeness_score(
    has_revised_cost: bool,
    has_expenditure: bool,
    has_physical_progress: bool,
    has_planned_completion: bool,
    has_narrative: bool,
) -> float:
    """Score based on how many required CUF fields are present."""
    fields = [has_revised_cost, has_expenditure, has_physical_progress, has_planned_completion, has_narrative]
    present = sum(1 for f in fields if f)
    return round(MAX_COMPONENT * present / len(fields), 2)


def _freshness_score(reporting_lag_days: int | None) -> tuple[float, list[str]]:
    """Score based on how recently the data was reported.

    Lag is days between reporting_month and submitted_at.
    """
    warnings: list[str] = []
    if reporting_lag_days is None:
        warnings.append("Reporting lag unknown; freshness scored at zero.")
        return 0.0, warnings

    if reporting_lag_days < 0:
        warnings.append("Submission date precedes reporting month; data freshness suspect.")
        return round(MAX_COMPONENT * 0.5, 2), warnings

    if reporting_lag_days <= 15:
        return MAX_COMPONENT, []
    if reporting_lag_days <= 30:
        return round(MAX_COMPONENT * 0.85, 2), []
    if reporting_lag_days <= 60:
        return round(MAX_COMPONENT * 0.6, 2), []
    if reporting_lag_days <= 90:
        warnings.append(f"Reporting lag is {reporting_lag_days} days; data may be stale.")
        return round(MAX_COMPONENT * 0.35, 2), warnings

    warnings.append(f"Reporting lag is {reporting_lag_days} days; data is severely outdated.")
    return round(MAX_COMPONENT * 0.1, 2), warnings


def _consistency_score(
    expenditure: float | None,
    revised_cost: float | None,
    physical_progress: float | None,
) -> tuple[float, list[str]]:
    """Deterministic internal consistency checks."""
    warnings: list[str] = []
    deductions = 0.0

    if expenditure is not None and revised_cost is not None and revised_cost > 0:
        spend_ratio = expenditure / revised_cost
        if spend_ratio > 1.15:
            deductions += 8
            warnings.append(f"Expenditure ({spend_ratio:.0%}) exceeds revised cost by >15%.")
        if physical_progress is not None:
            progress_ratio = physical_progress / 100.0
            gap = abs(spend_ratio - progress_ratio)
            if gap > 0.30:
                deductions += 6
                warnings.append(
                    f"Large gap ({gap:.0%}) between expenditure ratio and physical progress."
                )
    else:
        if expenditure is None:
            warnings.append("Expenditure data missing; consistency cannot be fully assessed.")
            deductions += 5
        if revised_cost is None:
            warnings.append("Revised cost data missing; consistency cannot be fully assessed.")
            deductions += 5

    if physical_progress is not None:
        if physical_progress < 0 or physical_progress > 100:
            deductions += 10
            warnings.append(f"Physical progress ({physical_progress}%) outside valid 0-100 range.")

    return round(max(0, MAX_COMPONENT - deductions), 2), warnings


def _reliability_score(
    agency_track_record: float | None,
    submission_count: int = 1,
) -> tuple[float, list[str]]:
    """Score based on historical agency reliability.

    agency_track_record: 0-1 reliability score from historical accuracy.
    If unavailable, default to a neutral mid-score with a warning.
    """
    warnings: list[str] = []

    if agency_track_record is None:
        warnings.append("Agency reliability history not available; scored at neutral baseline.")
        base = MAX_COMPONENT * 0.5
    else:
        base = MAX_COMPONENT * min(1.0, max(0.0, agency_track_record))

    # Bonus for consistent reporting history
    if submission_count >= 12:
        base = min(MAX_COMPONENT, base + 2)
    elif submission_count >= 6:
        base = min(MAX_COMPONENT, base + 1)
    elif submission_count <= 1:
        warnings.append("Only one submission on record; reliability assessment is limited.")

    return round(base, 2), warnings


def _confidence_label(score: float) -> str:
    if score >= 80:
        return "HIGH"
    if score >= 50:
        return "MODERATE"
    return "LOW"


def compute_dcs(
    *,
    has_revised_cost: bool = False,
    has_expenditure: bool = False,
    has_physical_progress: bool = False,
    has_planned_completion: bool = False,
    has_narrative: bool = False,
    reporting_lag_days: int | None = None,
    expenditure: float | None = None,
    revised_cost: float | None = None,
    physical_progress: float | None = None,
    agency_track_record: float | None = None,
    submission_count: int = 1,
) -> DCSResult:
    """Compute the Data Confidence Score from its four components."""
    all_warnings: list[str] = []

    completeness = _completeness_score(
        has_revised_cost, has_expenditure, has_physical_progress, has_planned_completion, has_narrative
    )

    freshness, fw = _freshness_score(reporting_lag_days)
    all_warnings.extend(fw)

    consistency, cw = _consistency_score(expenditure, revised_cost, physical_progress)
    all_warnings.extend(cw)

    reliability, rw = _reliability_score(agency_track_record, submission_count)
    all_warnings.extend(rw)

    total = round(completeness + freshness + consistency + reliability, 2)
    total = min(100.0, max(0.0, total))

    return DCSResult(
        dcs_score=total,
        completeness=completeness,
        freshness=freshness,
        consistency=consistency,
        reliability=reliability,
        confidence_label=_confidence_label(total),
        warning_flags=all_warnings,
    )
