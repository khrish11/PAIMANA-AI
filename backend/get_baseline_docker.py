"""Script to record baseline database counts using Docker exec."""

import subprocess
import json

def run_docker_query(query):
    cmd = f'docker exec infra-db-1 psql -U paimana -d paimana_ai -c "{query}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def get_baseline_counts():
    print("=" * 60)
    print("BASELINE DATABASE COUNTS")
    print("=" * 60)
    
    # Projects count
    projects = run_docker_query("SELECT COUNT(*) FROM projects")
    project_count = projects.split('\n')[2].strip()
    print(f"Projects: {project_count}")
    
    # CUF Submissions count
    submissions = run_docker_query("SELECT COUNT(*) FROM cuf_submissions")
    submission_count = submissions.split('\n')[2].strip()
    print(f"CUF Submissions: {submission_count}")
    
    # Latest reporting month
    latest = run_docker_query("SELECT reporting_month FROM cuf_submissions ORDER BY reporting_month DESC LIMIT 1")
    latest_month = latest.split('\n')[2].strip() if latest.split('\n')[2].strip() else "None"
    print(f"Latest Reporting Month: {latest_month}")
    
    # Risk scores count
    risks = run_docker_query("SELECT COUNT(*) FROM risk_scores")
    risk_count = risks.split('\n')[2].strip()
    print(f"Risk Scores: {risk_count}")
    
    # Audit log count
    audits = run_docker_query("SELECT COUNT(*) FROM audit_log")
    audit_count = audits.split('\n')[2].strip()
    print(f"Audit Log Entries: {audit_count}")
    
    # Governance actions count
    governance = run_docker_query("SELECT COUNT(*) FROM governance_actions")
    governance_count = governance.split('\n')[2].strip()
    print(f"Governance Actions: {governance_count}")
    
    # Import batches count
    try:
        imports = run_docker_query("SELECT COUNT(*) FROM import_batches")
        import_count = imports.split('\n')[2].strip() if len(imports.split('\n')) > 2 else "0"
        print(f"Import Batches: {import_count}")
    except:
        import_count = "0"
        print(f"Import Batches: 0 (table may not exist)")
    
    print("=" * 60)
    
    return {
        "projects": int(project_count) if project_count.isdigit() else 0,
        "submissions": int(submission_count) if submission_count.isdigit() else 0,
        "latest_month": latest_month if latest_month != "None" else None,
        "risk_scores": int(risk_count) if risk_count.isdigit() else 0,
        "audit_logs": int(audit_count) if audit_count.isdigit() else 0,
        "governance": int(governance_count) if governance_count.isdigit() else 0,
        "import_batches": int(import_count) if import_count.isdigit() else 0,
    }

if __name__ == "__main__":
    baseline = get_baseline_counts()
    print("\nBaseline JSON:")
    print(json.dumps(baseline, indent=2))
