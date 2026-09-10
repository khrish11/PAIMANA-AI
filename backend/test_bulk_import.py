import requests

BASE_URL = "http://localhost:8001"

headers = {
    "Content-Type": "application/json",
    "X-User-Role": "ANALYST",
    "X-Username": "test_analyst"
}

# CSV content for bulk import
csv_content = """project_code,reporting_month,physical_progress,expenditure,revised_cost,narrative
SIH-TEST-2026-001,2024-03-01,30.0,300000.0,1100000.0,Third month progress
SIH-TEST-2026-001,2024-04-01,40.0,400000.0,1150000.0,Fourth month progress
"""

print("=== Test 1: Preview Import ===")
params = {
    "csv_content": csv_content,
    "batch_name": "Test Import Batch",
    "import_method": "csv",
    "source_file": "test_import.csv"
}

resp = requests.post(f"{BASE_URL}/api/v1/data_operations/import/preview", params=params, headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Rows detected: {data.get('rows_detected')}")
    print(f"New projects: {data.get('new_projects')}")
    print(f"Existing projects: {data.get('existing_projects')}")
    print(f"New submissions: {data.get('new_submissions')}")
    print(f"Duplicate submissions: {data.get('duplicate_submissions')}")
    print(f"Revisions: {data.get('revisions')}")
    print(f"Invalid rows: {data.get('invalid_rows')}")
else:
    print(f"Error: {resp.text}")

print("\n=== Test 2: Execute Import ===")
execute_params = {
    "csv_content": csv_content,
    "batch_name": "Test Import Batch",
    "import_method": "csv",
    "source_file": "test_import.csv",
    "allow_revisions": False
}

resp = requests.post(f"{BASE_URL}/api/v1/data_operations/import/execute", params=execute_params, headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Batch ID: {data.get('batch_id')}")
    print(f"Status: {data.get('status')}")
    print(f"New submissions: {data.get('new_submissions')}")
    print(f"Invalid rows: {data.get('invalid_rows')}")
else:
    print(f"Error: {resp.text}")

print("\n=== Test 3: List Import Batches ===")
resp = requests.get(f"{BASE_URL}/api/v1/data_operations/import/batches", headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Total batches: {data.get('total_count')}")
    for batch in data.get('batches', [])[:3]:
        print(f"  Batch: {batch['batch_name']}, Status: {batch['status']}, New submissions: {batch['new_submissions']}")
else:
    print(f"Error: {resp.text}")

print("\n=== Test 4: Test Duplicate/Idempotency (re-run same import) ===")
resp = requests.post(f"{BASE_URL}/api/v1/data_operations/import/execute", params=execute_params, headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Status: {data.get('status')}")
    print(f"Duplicate submissions: {data.get('duplicate_submissions')}")
    print(f"New submissions: {data.get('new_submissions')}")
else:
    print(f"Error: {resp.text}")
