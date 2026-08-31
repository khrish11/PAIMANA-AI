from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session


RiskOverrunThreshold = Literal[0.05, 0.10, 0.20]


@dataclass(frozen=True)
class RCFResult:
    sector: str
    size_band: str
    region: str
    sample_count: int
    used_fallback: bool
    warning: str | None
    cost_overrun_p50: float
    cost_overrun_p80: float
    cost_overrun_p90: float
    schedule_delay_p50: float
    probability_overrun_gt_5: float
    probability_overrun_gt_10: float
    probability_overrun_gt_20: float


def size_band_for_cost(sanctioned_cost: float) -> str:
    if sanctioned_cost < 500:
        return "150-500 Cr"
    if sanctioned_cost < 2000:
        return "500-2000 Cr"
    return "2000+ Cr"


def get_completed_projects_from_db(session: Session) -> pd.DataFrame:
    """Query completed projects from PostgreSQL database.
    
    A project is considered completed if it has:
    - status indicating completion (e.g., 'Completed', 'Closed')
    - physical_progress >= 100
    - or has an actual completion date
    
    Returns DataFrame with columns needed for RCF analysis.
    """
    from app.models.projects import Project
    from app.models.cuf_submissions import CUFSubmission
    
    # Query projects with completion indicators
    query = (
        select(
            Project.project_id,
            Project.sector,
            Project.state,
            Project.sanctioned_cost,
            Project.status,
            func.max(CUFSubmission.revised_cost).label('revised_cost'),
            func.max(CUFSubmission.expenditure).label('expenditure'),
            func.max(CUFSubmission.physical_progress).label('physical_progress'),
            func.max(CUFSubmission.reporting_month).label('latest_reporting_month')
        )
        .join(CUFSubmission, Project.project_id == CUFSubmission.project_id)
        .group_by(Project.project_id, Project.sector, Project.state, Project.sanctioned_cost, Project.status)
    )
    
    result = session.execute(query).all()
    
    if not result:
        return pd.DataFrame()
    
    df = pd.DataFrame(result, columns=[
        'project_id', 'sector', 'state', 'sanctioned_cost', 'status',
        'revised_cost', 'expenditure', 'physical_progress', 'latest_reporting_month'
    ])
    
    # Filter for completed projects
    completed_mask = (
        (df['status'].str.lower().isin(['completed', 'closed', 'finished'])) |
        (df['physical_progress'] >= 100) |
        (df['expenditure'] >= df['sanctioned_cost'])
    )
    
    df_completed = df[completed_mask].copy()
    
    if df_completed.empty:
        return pd.DataFrame()
    
    # Calculate cost overrun ratio
    df_completed['sanctioned_cost'] = pd.to_numeric(df_completed['sanctioned_cost'], errors='coerce')
    df_completed['revised_cost'] = pd.to_numeric(df_completed['revised_cost'], errors='coerce')
    df_completed['expenditure'] = pd.to_numeric(df_completed['expenditure'], errors='coerce')
    
    # Use revised cost if available, otherwise use expenditure
    df_completed['final_cost'] = df_completed['revised_cost'].fillna(df_completed['expenditure'])
    
    # Calculate cost overrun ratio
    df_completed['cost_overrun_ratio'] = (
        (df_completed['final_cost'] - df_completed['sanctioned_cost']) / df_completed['sanctioned_cost']
    ).clip(lower=0)  # Only positive overruns
    
    # Add size band
    df_completed['size_band'] = df_completed['sanctioned_cost'].apply(size_band_for_cost)
    
    # Ensure state is not null
    df_completed['state'] = df_completed['state'].fillna('National')
    
    return df_completed


def fit_reference_class(
    completed_projects: pd.DataFrame | None = None,
    session: Session | None = None,
    *,
    sector: str | None = None,
    state: str | None = None,
    size_band: str | None = None,
    region: str | None = None,
    min_cluster_size: int = 15,
) -> RCFResult:
    """Fit empirical RCF quantiles using the SRS default minimum cluster size of 15.

    Accepts the dataframe as the first positional argument for compatibility with the
    test suite and historical API usage, while also supporting the keyword-only form
    used elsewhere in the app.
    """
    if completed_projects is None:
        if session is not None:
            try:
                completed_projects = get_completed_projects_from_db(session)
            except Exception as e:
                return RCFResult(
                    sector=sector or "",
                    size_band=size_band or "",
                    region=state or region or "",
                    sample_count=0,
                    used_fallback=True,
                    warning=f"Database query failed: {str(e)}",
                    cost_overrun_p50=0.10,
                    cost_overrun_p80=0.20,
                    cost_overrun_p90=0.30,
                    schedule_delay_p50=0.0,
                    probability_overrun_gt_5=0.0,
                    probability_overrun_gt_10=0.0,
                    probability_overrun_gt_20=0.0,
                )
        else:
            return RCFResult(
                sector=sector or "",
                size_band=size_band or "",
                region=state or region or "",
                sample_count=0,
                used_fallback=True,
                warning="No database session provided and no completed projects dataframe available",
                cost_overrun_p50=0.10,
                cost_overrun_p80=0.20,
                cost_overrun_p90=0.30,
                schedule_delay_p50=0.0,
                probability_overrun_gt_5=0.0,
                probability_overrun_gt_10=0.0,
                probability_overrun_gt_20=0.0,
            )

    if region is not None and state is None:
        state = region
    if state is None:
        state = region or "National"

    state_key = "state" if "state" in completed_projects.columns else "region"

    cluster = completed_projects[
        (completed_projects["sector"] == sector) &
        (completed_projects[state_key] == state) &
        (completed_projects["size_band"] == size_band)
    ] if sector and size_band else completed_projects.copy()

    used_fallback = len(cluster) < min_cluster_size
    warning = None

    if used_fallback and sector:
        cluster = completed_projects[completed_projects["sector"] == sector]
        warning = (
            "Reference-class cluster below 15 completed projects; "
            "using national-sector fallback as specified in SRS Section 6.4.2."
        )

    if cluster.empty:
        return RCFResult(
            sector=sector or "",
            size_band=size_band or "",
            region=state or region or "",
            sample_count=0,
            used_fallback=True,
            warning="No completed projects available for RCF fallback cluster",
            cost_overrun_p50=0.10,
            cost_overrun_p80=0.20,
            cost_overrun_p90=0.30,
            schedule_delay_p50=0.0,
            probability_overrun_gt_5=0.0,
            probability_overrun_gt_10=0.0,
            probability_overrun_gt_20=0.0,
        )

    if "cost_overrun_ratio" in cluster.columns:
        cost_overrun = cluster["cost_overrun_ratio"].astype(float).to_numpy()
        schedule_delay = cluster.get("schedule_delay_months", pd.Series(np.zeros(len(cluster)))).astype(float).to_numpy()
        p50 = float(np.quantile(cost_overrun, 0.50))
        p80 = float(np.quantile(cost_overrun, 0.80))
        p90 = float(np.quantile(cost_overrun, 0.90))
        return RCFResult(
            sector=sector or cluster["sector"].iloc[0],
            size_band=size_band or cluster["size_band"].iloc[0],
            region=state or region or cluster[state_key].iloc[0],
            sample_count=int(len(cluster)),
            used_fallback=used_fallback,
            warning=warning,
            cost_overrun_p50=p50,
            cost_overrun_p80=p80,
            cost_overrun_p90=p90,
            schedule_delay_p50=float(np.quantile(schedule_delay, 0.50)),
            probability_overrun_gt_5=float(np.mean(cost_overrun > 0.05)),
            probability_overrun_gt_10=float(np.mean(cost_overrun > 0.10)),
            probability_overrun_gt_20=float(np.mean(cost_overrun > 0.20)),
        )

    return RCFResult(
        sector=sector or "",
        size_band=size_band or "",
        region=state or region or "",
        sample_count=int(len(cluster)),
        used_fallback=True,
        warning="Cost overrun ratio not available in completed projects",
        cost_overrun_p50=0.10,
        cost_overrun_p80=0.20,
        cost_overrun_p90=0.30,
        schedule_delay_p50=0.0,
        probability_overrun_gt_5=0.0,
        probability_overrun_gt_10=0.0,
        probability_overrun_gt_20=0.0,
    )
