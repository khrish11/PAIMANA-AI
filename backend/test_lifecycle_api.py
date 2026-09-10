import requests
import json

BASE_URL = "http://localhost:8001"

# Headers for AGENCY role
agency_headers = {
    "Content-Type": "application/json",
    "X-User-Role": "AGENCY",
    "X-Username": "test_agency"
}

# Headers for ANALYST role
analyst_headers = {
    "Content-Type": "application/json",
    "X-User-Role": "ANALYST",
    "X-Username": "test_analyst"
}

print("=== Step 1: Create Project ===")
project_payload = {
    "project_code": "SIH-TEST-2026-001",
    "project_name": "Test Project for Continuous Operations",
    "sanctioned_cost": 1000000.0,
    "sector": "Infrastructure",
    "state": "Maharashtra",
    "ministry": "Ministry of Road Transport",
    "implementing_agency": "NHAI",
    "approved_date": "2024-01-01",
    "original_completion_date": "2026-12-31"
}

resp = requests.post(f"{BASE_URL}/api/v1/data_operations/projects", json=project_payload, headers=agency_headers)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
project_id = resp.json().get("project_id") if resp.status_code == 200 else None
print(f"Project ID: {project_id}")

if project_id:
    print("\n=== Step 2: Add Month 1 CUF ===")
    cuf1_payload = {
        "project_id": project_id,
        "reporting_month": "2024-01-01",
        "revised_cost": 1000000.0,
        "expenditure": 100000.0,
        "physical_progress": 10.0,
        "planned_completion": "2026-12-31",
        "narrative_text": "Initial progress",
        "submitted_by": "test_analyst"
    }
    resp1 = requests.post(f"{BASE_URL}/api/v1/data_operations/projects/{project_id}/submissions", json=cuf1_payload, headers=analyst_headers)
    print(f"Status: {resp1.status_code}")
    print(f"Response: {resp1.text[:200]}")

    print("\n=== Step 3: Add Month 2 CUF ===")
    cuf2_payload = {
        "project_id": project_id,
        "reporting_month": "2024-02-01",
        "revised_cost": 1050000.0,
        "expenditure": 200000.0,
        "physical_progress": 20.0,
        "planned_completion": "2026-12-31",
        "narrative_text": "Second month progress",
        "submitted_by": "test_analyst"
    }
    resp2 = requests.post(f"{BASE_URL}/api/v1/data_operations/projects/{project_id}/submissions", json=cuf2_payload, headers=analyst_headers)
    print(f"Status: {resp2.status_code}")
    print(f"Response: {resp2.text[:200]}")

    print("\n=== Step 4: Revise Month 2 CUF ===")
    cuf_rev_payload = {
        "project_id": project_id,
        "reporting_month": "2024-02-01",
        "revised_cost": 1070000.0,
        "expenditure": 220000.0,
        "physical_progress": 22.0,
        "planned_completion": "2026-12-31",
        "narrative_text": "Correction to second month",
        "submitted_by": "test_analyst"
    }
    resp3 = requests.post(f"{BASE_URL}/api/v1/data_operations/projects/{project_id}/submissions", json=cuf_rev_payload, headers=analyst_headers)
    print(f"Status: {resp3.status_code}")
    print(f"Response: {resp3.text[:200]}")

    print("\n=== Step 5: Get Project History ===")
    hist_resp = requests.get(f"{BASE_URL}/api/v1/data_operations/projects/{project_id}/history", headers=analyst_headers)
    print(f"Status: {hist_resp.status_code}")
    hist_data = hist_resp.json()
    print(f"History entries: {len(hist_data.get('history', []))}")
    for h in hist_data.get('history', []):
        print(f"  Month: {h['reporting_month']}, Version: {h['version']}, is_latest: {h['is_latest']}, superseded_by: {h['superseded_by']}")

print("\n=== Step 6: Check PostgreSQL Directly ===")
import psycopg2
conn = psycopg2.connect(host='localhost', port=5435, database='paimana_ai', user='paimana', password='paimanapass')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM projects')
print(f"Projects in DB: {cursor.fetchone()[0]}")
cursor.execute('SELECT COUNT(*) FROM cuf_submissions')
print(f"CUF submissions in DB: {cursor.fetchone()[0]}")
cursor.execute('SELECT COUNT(*) FROM risk_scores')
print(f"Risk scores in DB: {cursor.fetchone()[0]}")
cursor.execute('SELECT COUNT(*) FROM audit_log')
print(f"Audit logs in DB: {cursor.fetchone()[0]}")
cursor.close()
conn.close()
