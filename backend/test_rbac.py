import requests

BASE_URL = "http://localhost:8001"

# Test 1: AGENCY role can create project
print("=== Test 1: AGENCY can create project ===")
agency_headers = {
    "Content-Type": "application/json",
    "X-User-Role": "AGENCY",
    "X-Username": "test_agency"
}

project_payload = {
    "project_code": "SIH-TEST-2026-004",
    "project_name": "RBAC Test Project",
    "sanctioned_cost": 500000.0,
    "sector": "Infrastructure",
    "state": "Delhi",
    "ministry": "Ministry of Urban Development",
    "approved_date": "2024-01-01"
}

resp = requests.post(f"{BASE_URL}/api/v1/data_operations/projects", json=project_payload, headers=agency_headers)
print(f"Status: {resp.status_code}")
print(f"Expected: 200, Got: {resp.status_code}")
if resp.status_code == 200:
    print("PASS: AGENCY can create project")
else:
    print(f"FAIL: {resp.text}")

# Test 2: ANALYST role cannot create project
print("\n=== Test 2: ANALYST cannot create project ===")
analyst_headers = {
    "Content-Type": "application/json",
    "X-User-Role": "ANALYST",
    "X-Username": "test_analyst"
}

project_payload_2 = {
    "project_code": "SIH-TEST-2026-003",
    "project_name": "RBAC Test Project 2",
    "sanctioned_cost": 600000.0,
    "sector": "Infrastructure",
    "state": "Delhi",
    "ministry": "Ministry of Urban Development",
    "approved_date": "2024-01-01"
}

resp = requests.post(f"{BASE_URL}/api/v1/data_operations/projects", json=project_payload_2, headers=analyst_headers)
print(f"Status: {resp.status_code}")
print(f"Expected: 403, Got: {resp.status_code}")
if resp.status_code == 403:
    print("PASS: ANALYST cannot create project")
else:
    print(f"FAIL: {resp.text}")

# Test 3: No role (unauthorized) - should fail
print("\n=== Test 3: No role (unauthorized) ===")
no_role_headers = {
    "Content-Type": "application/json",
    "X-Username": "unauthorized_user"
}

resp = requests.post(f"{BASE_URL}/api/v1/data_operations/projects", json=project_payload, headers=no_role_headers)
print(f"Status: {resp.status_code}")
print(f"Expected: 401/403, Got: {resp.status_code}")
if resp.status_code in [401, 403]:
    print("PASS: Unauthorized user rejected")
else:
    print(f"FAIL: {resp.text}")

# Test 4: ANALYST can submit CUF
print("\n=== Test 4: ANALYST can submit CUF ===")
# Use existing project ID from previous test
cuf_payload = {
    "project_id": "0c35a4ed-10ac-4d9c-91d8-f5191c280c93",
    "reporting_month": "2024-05-01",
    "revised_cost": 1200000.0,
    "expenditure": 500000.0,
    "physical_progress": 50.0,
    "narrative_text": "RBAC test submission",
    "submitted_by": "test_analyst"
}

resp = requests.post(f"{BASE_URL}/api/v1/data_operations/projects/0c35a4ed-10ac-4d9c-91d8-f5191c280c93/submissions", json=cuf_payload, headers=analyst_headers)
print(f"Status: {resp.status_code}")
print(f"Expected: 200, Got: {resp.status_code}")
if resp.status_code == 200:
    print("PASS: ANALYST can submit CUF")
else:
    print(f"FAIL: {resp.text}")

# Test 5: AGENCY cannot submit CUF
print("\n=== Test 5: AGENCY cannot submit CUF ===")
resp = requests.post(f"{BASE_URL}/api/v1/data_operations/projects/0c35a4ed-10ac-4d9c-91d8-f5191c280c93/submissions", json=cuf_payload, headers=agency_headers)
print(f"Status: {resp.status_code}")
print(f"Expected: 403, Got: {resp.status_code}")
if resp.status_code == 403:
    print("PASS: AGENCY cannot submit CUF")
else:
    print(f"FAIL: {resp.text}")
