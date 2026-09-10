"""Script to record baseline database counts before testing."""

import sys
sys.path.insert(0, '.')

from app.db.session import SessionLocal
from app.models.projects import Project
from app.models.cuf_submissions import CUFSubmission
from app.models.risk_scores import RiskScore
from app.models.audit_log import AuditLog
from app.models.governance_actions import GovernanceAction
from app.models.import_batches import ImportBatch

def get_baseline_counts():
    db = SessionLocal()
    try:
        project_count = db.query(Project).count()
        submission_count = db.query(CUFSubmission).count()
        
        # Get latest reporting month
        latest_submission = db.query(CUFSubmission).order_by(
            CUFSubmission.reporting_month.desc()
        ).first()
        latest_month = latest_submission.reporting_month.isoformat() if latest_submission and latest_submission.reporting_month else None
        
        risk_score_count = db.query(RiskScore).count()
        audit_log_count = db.query(AuditLog).count()
        governance_count = db.query(GovernanceAction).count()
        import_batch_count = db.query(ImportBatch).count()
        
        print("=" * 60)
        print("BASELINE DATABASE COUNTS")
        print("=" * 60)
        print(f"Projects: {project_count}")
        print(f"CUF Submissions: {submission_count}")
        print(f"Latest Reporting Month: {latest_month}")
        print(f"Risk Scores: {risk_score_count}")
        print(f"Audit Log Entries: {audit_log_count}")
        print(f"Governance Queue Entries: {governance_count}")
        print(f"Import Batches: {import_batch_count}")
        print("=" * 60)
        
        return {
            "projects": project_count,
            "submissions": submission_count,
            "latest_month": latest_month,
            "risk_scores": risk_score_count,
            "audit_logs": audit_log_count,
            "governance": governance_count,
            "import_batches": import_batch_count,
        }
    finally:
        db.close()

if __name__ == "__main__":
    get_baseline_counts()
