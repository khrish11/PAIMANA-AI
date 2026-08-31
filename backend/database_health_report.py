"""Generate comprehensive database health report for PAIMANA data."""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.projects import Project
from app.models.cuf_submissions import CUFSubmission
from app.models.risk_scores import RiskScore
from datetime import datetime


def generate_health_report():
    """Generate comprehensive database health report."""
    session = SessionLocal()
    
    try:
        print("=" * 80)
        print("PAIMANA DATABASE HEALTH REPORT")
        print("=" * 80)
        print(f"Generated: {datetime.now().isoformat()}")
        print()
        
        # Project Statistics
        print("PROJECT STATISTICS")
        print("-" * 80)
        total_projects = session.query(func.count(Project.project_id)).scalar()
        print(f"Total Projects: {total_projects}")
        
        # Sector distribution
        sector_dist = session.query(
            Project.sector,
            func.count(Project.project_id)
        ).group_by(Project.sector).order_by(func.count(Project.project_id).desc()).all()
        
        print("\nSector Distribution (Top 15):")
        for sector, count in sector_dist[:15]:
            pct = (count / total_projects * 100) if total_projects > 0 else 0
            print(f"  {sector}: {count} ({pct:.1f}%)")
        
        # State distribution
        state_dist = session.query(
            Project.state,
            func.count(Project.project_id)
        ).group_by(Project.state).order_by(func.count(Project.project_id).desc()).all()
        
        print("\nState Distribution (Top 10):")
        for state, count in state_dist[:10]:
            pct = (count / total_projects * 100) if total_projects > 0 else 0
            print(f"  {state}: {count} ({pct:.1f}%)")
        
        # Ministry distribution
        ministry_dist = session.query(
            Project.ministry,
            func.count(Project.project_id)
        ).group_by(Project.ministry).order_by(func.count(Project.project_id).desc()).all()
        
        print("\nMinistry Distribution (Top 10):")
        for ministry, count in ministry_dist[:10]:
            pct = (count / total_projects * 100) if total_projects > 0 else 0
            print(f"  {ministry}: {count} ({pct:.1f}%)")
        
        # Cost distribution
        cost_stats = session.query(
            func.min(Project.sanctioned_cost),
            func.max(Project.sanctioned_cost),
            func.avg(Project.sanctioned_cost),
            func.sum(Project.sanctioned_cost)
        ).first()
        
        print("\nCost Statistics (in Crores):")
        print(f"  Min: ₹{cost_stats[0]:,.2f} Cr")
        print(f"  Max: ₹{cost_stats[1]:,.2f} Cr")
        print(f"  Avg: ₹{cost_stats[2]:,.2f} Cr")
        print(f"  Total: ₹{cost_stats[3]:,.2f} Cr")
        
        # Status distribution
        status_dist = session.query(
            Project.status,
            func.count(Project.project_id)
        ).group_by(Project.status).order_by(func.count(Project.project_id).desc()).all()
        
        print("\nStatus Distribution:")
        for status, count in status_dist:
            pct = (count / total_projects * 100) if total_projects > 0 else 0
            print(f"  {status}: {count} ({pct:.1f}%)")
        
        # Submission Statistics
        print("\n" + "=" * 80)
        print("SUBMISSION STATISTICS")
        print("-" * 80)
        total_submissions = session.query(func.count(CUFSubmission.submission_id)).scalar()
        print(f"Total Submissions: {total_submissions}")
        
        # Submissions per project
        submissions_per_project = session.query(
            func.count(CUFSubmission.submission_id)
        ).group_by(CUFSubmission.project_id).all()
        
        avg_submissions = sum([s[0] for s in submissions_per_project]) / len(submissions_per_project) if submissions_per_project else 0
        max_submissions = max([s[0] for s in submissions_per_project]) if submissions_per_project else 0
        min_submissions = min([s[0] for s in submissions_per_project]) if submissions_per_project else 0
        
        print(f"Submissions per Project:")
        print(f"  Average: {avg_submissions:.1f}")
        print(f"  Min: {min_submissions}")
        print(f"  Max: {max_submissions}")
        
        # Date range
        date_range = session.query(
            func.min(CUFSubmission.reporting_month),
            func.max(CUFSubmission.reporting_month)
        ).first()
        
        print(f"\nReporting Period:")
        print(f"  From: {date_range[0]}")
        print(f"  To: {date_range[1]}")
        
        # Physical progress distribution
        progress_stats = session.query(
            func.min(CUFSubmission.physical_progress),
            func.max(CUFSubmission.physical_progress),
            func.avg(CUFSubmission.physical_progress)
        ).first()
        
        print(f"\nPhysical Progress Statistics:")
        print(f"  Min: {progress_stats[0]:.1f}%")
        print(f"  Max: {progress_stats[1]:.1f}%")
        print(f"  Avg: {progress_stats[2]:.1f}%")
        
        # Expenditure statistics
        exp_stats = session.query(
            func.min(CUFSubmission.expenditure),
            func.max(CUFSubmission.expenditure),
            func.avg(CUFSubmission.expenditure),
            func.sum(CUFSubmission.expenditure)
        ).first()
        
        print(f"\nExpenditure Statistics (in Crores):")
        print(f"  Min: ₹{exp_stats[0]:,.2f} Cr")
        print(f"  Max: ₹{exp_stats[1]:,.2f} Cr")
        print(f"  Avg: ₹{exp_stats[2]:,.2f} Cr")
        print(f"  Total: ₹{exp_stats[3]:,.2f} Cr")
        
        # Narrative coverage
        narrative_count = session.query(func.count(CUFSubmission.submission_id)).filter(
            CUFSubmission.narrative_text.isnot(None),
            CUFSubmission.narrative_text != ''
        ).scalar()
        
        narrative_pct = (narrative_count / total_submissions * 100) if total_submissions > 0 else 0
        print(f"\nNarrative Coverage:")
        print(f"  Submissions with narrative: {narrative_count} ({narrative_pct:.1f}%)")
        
        # Risk Score Statistics
        print("\n" + "=" * 80)
        print("RISK SCORE STATISTICS")
        print("-" * 80)
        total_risk_scores = session.query(func.count(RiskScore.score_id)).scalar()
        print(f"Total Risk Scores: {total_risk_scores}")
        
        # Risk category distribution
        risk_dist = session.query(
            RiskScore.risk_category,
            func.count(RiskScore.score_id)
        ).group_by(RiskScore.risk_category).order_by(func.count(RiskScore.score_id).desc()).all()
        
        print("\nRisk Category Distribution:")
        for category, count in risk_dist:
            pct = (count / total_risk_scores * 100) if total_risk_scores > 0 else 0
            print(f"  {category}: {count} ({pct:.1f}%)")
        
        # Risk score statistics
        risk_stats = session.query(
            func.min(RiskScore.composite_score),
            func.max(RiskScore.composite_score),
            func.avg(RiskScore.composite_score)
        ).first()
        
        print(f"\nComposite Score Statistics:")
        print(f"  Min: {risk_stats[0]:.1f}")
        print(f"  Max: {risk_stats[1]:.1f}")
        print(f"  Avg: {risk_stats[2]:.1f}")
        
        # Component averages
        component_stats = session.query(
            func.avg(RiskScore.cost_risk),
            func.avg(RiskScore.schedule_risk),
            func.avg(RiskScore.progress_anomaly_score),
            func.avg(RiskScore.governance_risk),
            func.avg(RiskScore.data_confidence_score)
        ).first()
        
        print(f"\nComponent Averages:")
        print(f"  Cost Risk: {component_stats[0]:.1f}")
        print(f"  Schedule Risk: {component_stats[1]:.1f}")
        print(f"  Progress Anomaly: {component_stats[2]:.1f}")
        print(f"  Governance Risk: {component_stats[3]:.1f}")
        print(f"  Data Confidence: {component_stats[4]:.1f}")
        
        # Data Quality Metrics
        print("\n" + "=" * 80)
        print("DATA QUALITY METRICS")
        print("-" * 80)
        
        # Missing sector
        missing_sector = session.query(func.count(Project.project_id)).filter(
            Project.sector == 'Unknown'
        ).scalar()
        missing_sector_pct = (missing_sector / total_projects * 100) if total_projects > 0 else 0
        print(f"Projects with Unknown Sector: {missing_sector} ({missing_sector_pct:.1f}%)")
        
        # Missing ministry
        missing_ministry = session.query(func.count(Project.project_id)).filter(
            Project.ministry == 'Unknown'
        ).scalar()
        missing_ministry_pct = (missing_ministry / total_projects * 100) if total_projects > 0 else 0
        print(f"Projects with Unknown Ministry: {missing_ministry} ({missing_ministry_pct:.1f}%)")
        
        # Missing state
        missing_state = session.query(func.count(Project.project_id)).filter(
            Project.state == 'Unknown'
        ).scalar()
        missing_state_pct = (missing_state / total_projects * 100) if total_projects > 0 else 0
        print(f"Projects with Unknown State: {missing_state} ({missing_state_pct:.1f}%)")
        
        # Projects without submissions
        projects_without_submissions = session.query(func.count(Project.project_id)).filter(
            ~Project.project_id.in_(
                session.query(CUFSubmission.project_id).distinct()
            )
        ).scalar()
        no_sub_pct = (projects_without_submissions / total_projects * 100) if total_projects > 0 else 0
        print(f"Projects without Submissions: {projects_without_submissions} ({no_sub_pct:.1f}%)")
        
        # Projects without risk scores
        projects_without_risk = session.query(func.count(Project.project_id)).filter(
            ~Project.project_id.in_(
                session.query(RiskScore.project_id).distinct()
            )
        ).scalar()
        no_risk_pct = (projects_without_risk / total_projects * 100) if total_projects > 0 else 0
        print(f"Projects without Risk Scores: {projects_without_risk} ({no_risk_pct:.1f}%)")
        
        print("\n" + "=" * 80)
        print("REPORT COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error generating report: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    generate_health_report()
