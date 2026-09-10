import pytest
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, date

from app.models.projects import Project
from app.models.cuf_submissions import CUFSubmission
from app.models.risk_scores import RiskScore
from app.models.audit_log import AuditLog
from app.models.cuf_revisions import CUFRevision

from app.main import app
from app.db.session import SessionLocal
from fastapi.testclient import TestClient
from app.core.security import get_current_user, Role

TEST_PROJECT_PREFIX = "SIH-TEST-2026-"

@pytest.fixture
def client():
    from app.core.security import Role
    mock_user = {
        "username": "tester",
        "role": Role.ADMIN,  # Must be actual Role enum, not MagicMock
        "role_name": "admin",
        "agency": None,
    }
    app.dependency_overrides[get_current_user] = lambda: mock_user
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def auth_headers():
    return {
        "X-User-Role": "admin",
        "X-Username": "tester"
    }

@pytest.fixture
def cleanup_test_records(db_session):
    """Cleanup test records after test runs, even on failure."""
    test_project_ids = []
    yield test_project_ids
    
    # Cleanup: delete all test records
    for project_id in test_project_ids:
        try:
            # Delete in order of dependencies
            db_session.query(CUFRevision).filter(
                CUFRevision.submission_id.in_(
                    db_session.query(CUFSubmission.submission_id).filter(
                        CUFSubmission.project_id == project_id
                    )
                )
            ).delete(synchronize_session=False)
            
            db_session.query(CUFSubmission).filter(
                CUFSubmission.project_id == project_id
            ).delete(synchronize_session=False)
            
            db_session.query(RiskScore).filter(
                RiskScore.project_id == project_id
            ).delete(synchronize_session=False)
            
            db_session.query(AuditLog).filter(
                AuditLog.entity_id == project_id
            ).delete(synchronize_session=False)
            
            db_session.query(Project).filter(
                Project.project_id == project_id
            ).delete(synchronize_session=False)
            
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            print(f"Cleanup error for project {project_id}: {e}")

def test_continuous_operations_e2e(client, db_session, auth_headers, cleanup_test_records):
    # Generate isolated test project code
    test_suffix = str(uuid4())[:8]
    project_code = f"{TEST_PROJECT_PREFIX}{test_suffix}"
    
    # 1. Create a dummy project in the database
    project_id = str(uuid4())
    project = Project(
        project_id=project_id,
        project_name="Test Continuous Operations",
        project_code=project_code,
        ministry="Test Ministry",
        sector="Test Sector",
        state="Test State",
        sanctioned_cost=1000.0,
        approved_date=date(2022, 1, 15),
        status="ongoing",
        original_completion_date=date(2025, 12, 31)
    )
    db_session.add(project)
    db_session.commit()
    
    # Track for cleanup
    cleanup_test_records.append(project_id)

    # 2. First CUF Submission
    first_payload = {
        "project_id": project_id,
        "reporting_month": "2023-01-01",
        "revised_cost": 1100.0,
        "expenditure": 100.0,
        "physical_progress": 10.0,
        "planned_completion": "2025-12-31",
        "narrative_text": "Initial progress",
        "submitted_by": "tester"
    }

    resp1 = client.post("/api/v1/submissions", json=first_payload, headers=auth_headers)
    assert resp1.status_code == 200, resp1.text
    data1 = resp1.json()
    assert data1["status"] == "CREATED"
    assert "dcs_score" in data1
    assert "risk_score" in data1
    assert data1["version"] == 1

    # Verify database state after first submission
    subs1 = db_session.query(CUFSubmission).filter(CUFSubmission.project_id == project_id).all()
    assert len(subs1) == 1
    assert subs1[0].is_latest is True
    assert subs1[0].version == 1

    # 3. Second CUF Submission (New Month)
    second_payload = {
        "project_id": project_id,
        "reporting_month": "2023-02-01",
        "revised_cost": 1200.0,
        "expenditure": 200.0,
        "physical_progress": 20.0,
        "planned_completion": "2026-06-30",
        "narrative_text": "Further progress",
        "submitted_by": "tester"
    }

    resp2 = client.post("/api/v1/submissions", json=second_payload, headers=auth_headers)
    assert resp2.status_code == 200, resp2.text
    data2 = resp2.json()
    assert data2["status"] == "CREATED"
    assert data2["version"] == 1

    # Verify is_latest shifted correctly
    db_session.expire_all()
    subs2 = db_session.query(CUFSubmission).filter(
        CUFSubmission.project_id == project_id
    ).order_by(CUFSubmission.reporting_month).all()
    
    assert len(subs2) == 2
    assert subs2[0].reporting_month.isoformat() == "2023-01-01"
    assert subs2[0].is_latest is False
    assert subs2[1].reporting_month.isoformat() == "2023-02-01"
    assert subs2[1].is_latest is True

    # 4. Third CUF Submission (Revision of Second Month)
    revision_payload = {
        "project_id": project_id,
        "reporting_month": "2023-02-01",
        "revised_cost": 1250.0,
        "expenditure": 250.0,
        "physical_progress": 25.0,
        "planned_completion": "2026-06-30",
        "narrative_text": "Correction",
        "submitted_by": "tester"
    }

    resp3 = client.post("/api/v1/submissions", json=revision_payload, headers=auth_headers)
    assert resp3.status_code == 200, resp3.text
    data3 = resp3.json()
    assert data3["version"] == 2

    db_session.expire_all()
    subs3 = db_session.query(CUFSubmission).filter(
        CUFSubmission.project_id == project_id,
        CUFSubmission.reporting_month == "2023-02-01"
    ).order_by(CUFSubmission.version).all()
    
    assert len(subs3) == 2
    assert subs3[0].version == 1
    assert subs3[0].is_latest is False
    assert subs3[0].superseded_by is not None
    assert subs3[1].version == 2
    assert subs3[1].is_latest is True

    # 5. Project Detail and History endpoints
    detail_resp = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["project_id"] == str(project_id)

    history_resp = client.get(f"/api/v1/projects/{project_id}/history", headers=auth_headers)
    assert history_resp.status_code == 200
    history_data = history_resp.json()
    assert "history" in history_data
    assert len(history_data["history"]) == 3
    
    latest_hist = [h for h in history_data["history"] if h["is_latest"]]
    assert len(latest_hist) == 1
    assert latest_hist[0]["reporting_month"] == "2023-02-01"
    assert latest_hist[0]["version"] == 2
