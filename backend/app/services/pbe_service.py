"""Peer-Pressure Benchmarking Engine (PBE) service.

Identifies stage-aware peer cohorts, computes PPI score and percentile,
peer-relative cost/schedule variances, and returns anonymised peer data.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class PeerInfo:
    anonymised_id: str
    cost_variance: float
    schedule_variance: float
    physical_progress: float
    risk_category: str


@dataclass(frozen=True)
class PBEResult:
    project_id: str
    ppi_score: float
    percentile: float
    cohort_size: int
    cohort_sector: str
    cohort_size_band: str
    peer_relative_cost_variance: float
    peer_relative_schedule_variance: float
    peer_reporting_quality: float
    cohort_median_cost_overrun: float
    cohort_range_min: float
    cohort_range_max: float
    anonymised_peers: list[PeerInfo]
    explanation: str
    stage_normalised: bool


def _anonymise_id(project_id: str) -> str:
    """Create an anonymised, non-reversible identifier for peer display."""
    h = hashlib.sha256(f"pbe_anonymise_{project_id}".encode()).hexdigest()[:8]
    return f"PEER-{h.upper()}"


def _compute_ppi(
    own_cost_overrun: float,
    own_schedule_slip: float,
    peer_median_cost_overrun: float,
    peer_median_schedule_slip: float,
) -> float:
    """Peer Performance Index: 0-100.

    100 = project is performing perfectly relative to peers.
    50 = at peer median.
    0 = worst in cohort.
    """
    cost_diff = own_cost_overrun - peer_median_cost_overrun
    schedule_diff = own_schedule_slip - peer_median_schedule_slip

    # Normalise: negative diff (better than peers) → higher PPI
    cost_component = max(0, min(50, 25 - cost_diff * 100))
    schedule_component = max(0, min(50, 25 - schedule_diff * 5))

    return round(cost_component + schedule_component, 2)


def _percentile_rank(own_value: float, peer_values: list[float]) -> float:
    """Compute percentile rank (0-100) of own_value within peer_values."""
    if not peer_values:
        return 50.0
    count_below = sum(1 for v in peer_values if v < own_value)
    count_equal = sum(1 for v in peer_values if v == own_value)
    percentile = (count_below + 0.5 * count_equal) / len(peer_values) * 100
    return round(min(100, max(0, percentile)), 2)


def compute_pbe(
    *,
    project_id: str,
    own_cost_overrun: float,
    own_schedule_slip: float,
    own_physical_progress: float,
    own_reporting_lag: int,
    own_sector: str,
    own_size_band: str,
    peers: list[dict],
) -> PBEResult:
    """Compute PBE analysis for a project against its stage-aware peer cohort.

    peers: list of dicts with keys:
        project_id, cost_overrun_ratio, schedule_slip_months,
        physical_progress, reporting_lag_days, risk_category
    """
    # Filter peer cohort: same sector + size_band (stage-aware)
    cohort = [
        p for p in peers
        if p.get("sector") == own_sector
        and p.get("size_band") == own_size_band
        and str(p.get("project_id")) != str(project_id)
    ]

    if not cohort:
        return PBEResult(
            project_id=str(project_id),
            ppi_score=50.0,
            percentile=50.0,
            cohort_size=0,
            cohort_sector=own_sector,
            cohort_size_band=own_size_band,
            peer_relative_cost_variance=0.0,
            peer_relative_schedule_variance=0.0,
            peer_reporting_quality=0.0,
            cohort_median_cost_overrun=own_cost_overrun,
            cohort_range_min=own_cost_overrun,
            cohort_range_max=own_cost_overrun,
            anonymised_peers=[],
            explanation="No peers found in the same sector and size band for comparison.",
            stage_normalised=True,
        )

    peer_cost_overruns = [float(p.get("cost_overrun_ratio", 1.0)) for p in cohort]
    peer_schedule_slips = [float(p.get("schedule_slip_months", 0)) for p in cohort]
    peer_reporting_lags = [int(p.get("reporting_lag_days", 30)) for p in cohort]

    peer_median_cost = sorted(peer_cost_overruns)[len(peer_cost_overruns) // 2]
    peer_median_schedule = sorted(peer_schedule_slips)[len(peer_schedule_slips) // 2]

    ppi = _compute_ppi(own_cost_overrun, own_schedule_slip, peer_median_cost, peer_median_schedule)

    # Percentile: lower cost_overrun is better, so we rank inversely
    # (100th percentile = best performing = lowest cost overrun)
    percentile = 100 - _percentile_rank(own_cost_overrun, peer_cost_overruns)

    cost_variance = round(own_cost_overrun - peer_median_cost, 4)
    schedule_variance = round(own_schedule_slip - peer_median_schedule, 2)

    avg_peer_lag = sum(peer_reporting_lags) / len(peer_reporting_lags) if peer_reporting_lags else 30
    reporting_quality = round(max(0, min(100, 100 - (own_reporting_lag - avg_peer_lag) * 2)), 2)

    anonymised = [
        PeerInfo(
            anonymised_id=_anonymise_id(str(p.get("project_id", ""))),
            cost_variance=round(float(p.get("cost_overrun_ratio", 1.0)) - 1.0, 4),
            schedule_variance=round(float(p.get("schedule_slip_months", 0)), 2),
            physical_progress=round(float(p.get("physical_progress", 0)), 2),
            risk_category=str(p.get("risk_category", "MODERATE")),
        )
        for p in cohort[:10]  # Cap displayed peers
    ]

    if own_cost_overrun > peer_median_cost:
        position = "above the peer median"
        suggestion = "Consider reviewing cost drivers relative to peer benchmarks."
    elif own_cost_overrun < peer_median_cost:
        position = "below the peer median"
        suggestion = "Project is performing better than most peers on cost control."
    else:
        position = "at the peer median"
        suggestion = "Project cost performance is typical for its cohort."

    explanation = (
        f"Project sits at the {percentile:.0f}th percentile of {len(cohort)} peers "
        f"in {own_sector} / {own_size_band}. "
        f"Cost overrun ratio ({own_cost_overrun:.2%}) is {position} "
        f"({peer_median_cost:.2%}). {suggestion}"
    )

    return PBEResult(
        project_id=str(project_id),
        ppi_score=ppi,
        percentile=percentile,
        cohort_size=len(cohort),
        cohort_sector=own_sector,
        cohort_size_band=own_size_band,
        peer_relative_cost_variance=cost_variance,
        peer_relative_schedule_variance=schedule_variance,
        peer_reporting_quality=reporting_quality,
        cohort_median_cost_overrun=round(peer_median_cost, 4),
        cohort_range_min=round(min(peer_cost_overruns), 4),
        cohort_range_max=round(max(peer_cost_overruns), 4),
        anonymised_peers=anonymised,
        explanation=explanation,
        stage_normalised=True,
    )
