"""National dashboard and public summary API routes."""

from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.projects import Project
from app.models.cuf_submissions import CUFSubmission
from app.models.risk_scores import RiskScore
from app.schemas.schemas import (
    AlertItem,
    KPIRow,
    NationalDashboardResponse,
    PublicSummaryResponse,
    SectorOverrunStat,
    SectorRisk,
    StateRisk,
    StateTrend,
    TopRiskProject,
)

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/national", response_model=NationalDashboardResponse)
def national_dashboard(
    user: Any = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """National-level risk dashboard with KPIs, sector/state breakdown, top risks, and alerts."""
    # Query projects with their risk scores
    projects = db.query(Project).all()
    
    enriched = []
    for p in projects:
        # Get latest risk score
        latest_risk = db.query(RiskScore).filter(
            RiskScore.project_id == p.project_id
        ).order_by(RiskScore.reporting_month.desc()).first()
        
        if latest_risk:
            enriched.append({
                "project_id": str(p.project_id),
                "project_name": f"Project {p.project_id}",
                "sector": p.sector,
                "state": p.state,
                "sanctioned_cost": float(p.sanctioned_cost),
                "_risk": latest_risk,
                "_dcs": latest_risk.data_confidence_score,
            })
    
    total = len(enriched)
    high_risk = sum(1 for e in enriched if e["_risk"].risk_category in ("HIGH", "VERY_HIGH", "CRITICAL"))
    very_high_critical = sum(1 for e in enriched if e["_risk"].risk_category in ("VERY_HIGH", "CRITICAL"))
    avg_risk = sum(float(e["_risk"].composite_score) for e in enriched) / max(1, total)
    avg_dcs = sum(float(e["_dcs"]) for e in enriched) / max(1, total)
    requiring_review = sum(1 for e in enriched if e["_risk"].risk_category in ("HIGH", "VERY_HIGH", "CRITICAL"))

    # Sector breakdown
    sector_map: dict[str, list] = {}
    for e in enriched:
        sector_map.setdefault(e["sector"], []).append(e)

    sector_risks = [
        SectorRisk(
            sector=s,
            avg_risk=round(sum(float(e["_risk"].composite_score) for e in items) / len(items), 2),
            project_count=len(items),
        )
        for s, items in sorted(sector_map.items(), key=lambda x: -len(x[1]))[:15]
    ]

    # State breakdown
    state_map: dict[str, list] = {}
    for e in enriched:
        state_map.setdefault(e["state"], []).append(e)

    state_risks = [
        StateRisk(
            state=s,
            project_count=len(items),
            avg_risk=round(sum(float(e["_risk"].composite_score) for e in items) / len(items), 2),
            high_risk_count=sum(1 for e in items if e["_risk"].risk_category in ("HIGH", "VERY_HIGH", "CRITICAL")),
            avg_dcs=round(sum(float(e["_dcs"]) for e in items) / len(items), 2),
        )
        for s, items in sorted(state_map.items())
    ]

    # Top 10 by risk
    sorted_by_risk = sorted(enriched, key=lambda e: -float(e["_risk"].composite_score))[:10]
    top_risk = [
        TopRiskProject(
            project_id=e["project_id"],
            project_name=e["project_name"],
            ministry=p.ministry if (p := db.query(Project).filter(Project.project_id == e["project_id"]).first()) else "Unknown",
            sector=e["sector"],
            state=e["state"],
            risk_score=float(e["_risk"].composite_score),
            risk_category=e["_risk"].risk_category,
            dcs_score=float(e["_dcs"]),
            top_driver="N/A",  # SHAP not available in DB
        )
        for e in sorted_by_risk
    ]

    # Alerts
    alerts = []
    critical_count = sum(1 for e in enriched if e["_risk"].risk_category == "CRITICAL")
    if critical_count:
        alerts.append(AlertItem(
            alert_type="critical_risk",
            severity="CRITICAL",
            message=f"{critical_count} project(s) at CRITICAL risk level.",
            timestamp="2026-03-15T00:00:00Z",
        ))
    if requiring_review > 5:
        alerts.append(AlertItem(
            alert_type="governance_queue",
            severity="HIGH",
            message=f"{requiring_review} projects require governance review.",
            timestamp="2026-03-15T00:00:00Z",
        ))

    return NationalDashboardResponse(
        kpi=KPIRow(
            total_projects=total,
            high_risk_count=high_risk,
            very_high_critical_count=very_high_critical,
            avg_composite_risk=round(avg_risk, 2),
            avg_dcs=round(avg_dcs, 2),
            projects_requiring_review=requiring_review,
        ),
        sector_risks=sector_risks,
        state_risks=state_risks,
        top_risk_projects=top_risk,
        alerts=alerts,
        data_source="REAL_PAIMANA",
        reporting_period="2026-03",
    )


@router.get("/public/summary", response_model=PublicSummaryResponse)
def public_summary(db: Session = Depends(get_db)):
    """Public-safe aggregated summary with no project-level or agency-sensitive data."""
    projects = db.query(Project).all()

    sector_map: dict[str, list] = {}
    for p in projects:
        sector_map.setdefault(p.sector, []).append(p)

    sector_stats = []
    for sector, items in sorted(sector_map.items(), key=lambda x: -len(x[1]))[:15]:
        overruns = []
        for p in items:
            # Get latest submission for cost overrun calculation
            latest_submission = db.query(CUFSubmission).filter(
                CUFSubmission.project_id == p.project_id
            ).order_by(CUFSubmission.reporting_month.desc()).first()
            
            if latest_submission and latest_submission.revised_cost and p.sanctioned_cost > 0:
                overrun_ratio = float(latest_submission.revised_cost) / float(p.sanctioned_cost)
                overruns.append(overrun_ratio)
        avg_overrun = sum(overruns) / len(overruns) if overruns else 0
        sector_stats.append(SectorOverrunStat(
            sector=sector,
            avg_cost_overrun_pct=round(avg_overrun, 2),
            avg_schedule_delay_months=round(max(0, avg_overrun * 0.18), 1),
            project_count=len(items),
        ))

    state_map: dict[str, list] = {}
    for p in projects:
        state_map.setdefault(p.state, []).append(p)

    state_trends = []
    for state, items in sorted(state_map.items()):
        # Get risk scores for projects in this state
        risk_scores = []
        for p in items[:50]:
            latest_risk = db.query(RiskScore).filter(
                RiskScore.project_id == p.project_id
            ).order_by(RiskScore.reporting_month.desc()).first()
            if latest_risk:
                risk_scores.append(float(latest_risk.composite_score))
        avg_r = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        state_trends.append(StateTrend(state=state, avg_risk=round(avg_r, 2), project_count=len(items)))

    # Overall average risk
    all_risks = []
    for p in projects[:200]:
        latest_risk = db.query(RiskScore).filter(
            RiskScore.project_id == p.project_id
        ).order_by(RiskScore.reporting_month.desc()).first()
        if latest_risk:
            all_risks.append(float(latest_risk.composite_score))
    overall_avg_risk = sum(all_risks) / len(all_risks) if all_risks else 0

    # Overall average cost overrun
    all_overruns = []
    for p in projects:
        latest_submission = db.query(CUFSubmission).filter(
            CUFSubmission.project_id == p.project_id
        ).order_by(CUFSubmission.reporting_month.desc()).first()
        if latest_submission and latest_submission.revised_cost and p.sanctioned_cost > 0:
            overrun_ratio = (float(latest_submission.revised_cost) / float(p.sanctioned_cost) - 1) * 100
            all_overruns.append(overrun_ratio)
    overall_avg_overrun = sum(all_overruns) / len(all_overruns) if all_overruns else 0

    return PublicSummaryResponse(
        sector_overrun_stats=sector_stats,
        state_trends=state_trends,
        total_projects=len(projects),
        overall_avg_risk=round(overall_avg_risk, 2),
        overall_avg_cost_overrun_pct=round(overall_avg_overrun, 2),
        data_source="REAL_PAIMANA",
    )
