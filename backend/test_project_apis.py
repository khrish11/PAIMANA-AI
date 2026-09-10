import requests
import json

BASE_URL = "http://localhost:8001"
project_id = "0c35a4ed-10ac-4d9c-91d8-f5191c280c93"  # From previous test

headers = {
    "Content-Type": "application/json",
    "X-User-Role": "ANALYST",
    "X-Username": "test_analyst"
}

print("=== Test 1: GET Project Detail ===")
resp = requests.get(f"{BASE_URL}/api/v1/projects/{project_id}", headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Project ID: {data.get('project_id')}")
    print(f"Project Name: {data.get('project_name')}")
    print(f"Status: {data.get('status')}")
else:
    print(f"Error: {resp.text}")

print("\n=== Test 2: GET Project History (projects router) ===")
resp = requests.get(f"{BASE_URL}/api/v1/projects/{project_id}/history", headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"History entries: {len(data.get('history', []))}")
    for h in data.get('history', [])[:3]:
        print(f"  Month: {h['reporting_month']}, Version: {h['version']}, is_latest: {h['is_latest']}")
else:
    print(f"Error: {resp.text}")

print("\n=== Test 3: GET Project History (data_operations router) ===")
resp = requests.get(f"{BASE_URL}/api/v1/data_operations/projects/{project_id}/history", headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"History entries: {len(data.get('history', []))}")
    for h in data.get('history', [])[:3]:
        print(f"  Month: {h['reporting_month']}, Version: {h['version']}, is_latest: {h['is_latest']}, superseded_by: {h.get('superseded_by')}")
else:
    print(f"Error: {resp.text}")

print("\n=== Test 4: GET Project Risk ===")
resp = requests.get(f"{BASE_URL}/api/v1/projects/{project_id}/risk", headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Composite Score: {data.get('composite_score')}")
    print(f"Risk Category: {data.get('risk_category')}")
    print(f"DCS Score: {data.get('dcs', {}).get('dcs_score')}")
else:
    print(f"Error: {resp.text}")

print("\n=== Test 5: GET Project Trend ===")
resp = requests.get(f"{BASE_URL}/api/v1/projects/{project_id}/trend", headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Trend points: {len(data.get('trend', []))}")
else:
    print(f"Error: {resp.text}")

print("\n=== Test 6: List Projects ===")
resp = requests.get(f"{BASE_URL}/api/v1/projects", headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"Total projects: {data.get('total_count')}")
    print(f"Projects returned: {len(data.get('projects', []))}")
else:
    print(f"Error: {resp.text}")
