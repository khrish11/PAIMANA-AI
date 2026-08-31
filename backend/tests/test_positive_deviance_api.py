import pytest
from uuid import uuid4
from datetime import date, datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.mark.db
class TestPositiveDevianceAPI:
    """Test PDR API endpoints."""

    @pytest.fixture
    def client(self):
        from app.main import app
        return TestClient(app)

    @pytest.fixture
    def mock_positive_deviants(self):
        """Mock positive deviants data."""
        return {
            "positive_deviants": [
                {
                    "deviant_id": uuid4(),
                    "project_id": uuid4(),
                    "project_name": "Highway Project A",
                    "sector": "Roads",
                    "state": "Uttar Pradesh",
                    "reference_class_id": uuid4(),
                    "reporting_month": "2026-03-01",
                    "residual_cost_zscore": -1.8,
                    "residual_schedule_zscore": -2.1,
                    "data_confidence_score": 85,
                    "detected_at": "2026-03-15T10:00:00",
                },
                {
                    "deviant_id": uuid4(),
                    "project_id": uuid4(),
                    "project_name": "Highway Project B",
                    "sector": "Roads",
                    "state": "Bihar",
                    "reference_class_id": uuid4(),
                    "reporting_month": "2026-03-01",
                    "residual_cost_zscore": -1.5,
                    "residual_schedule_zscore": -1.7,
                    "data_confidence_score": 78,
                    "detected_at": "2026-03-15T10:00:00",
                },
            ],
            "metadata": {
                "total_count": 2,
                "sectors": ["Roads"],
                "states": ["Uttar Pradesh", "Bihar"],
            },
        }

    @pytest.fixture
    def mock_playbooks(self):
        """Mock playbooks data."""
        return {
            "playbooks": [
                {
                    "playbook_id": uuid4(),
                    "category": "land_acquisition",
                    "label": "Weekly coordination with district administration",
                    "confidence_tier": "HIGH",
                    "source_project_count": 8,
                    "created_at": "2026-03-15T10:00:00",
                    "last_updated_at": "2026-03-15T10:00:00",
                },
                {
                    "playbook_id": uuid4(),
                    "category": "contractor_management",
                    "label": "Regular contractor performance reviews",
                    "confidence_tier": "MEDIUM",
                    "source_project_count": 5,
                    "created_at": "2026-03-15T10:00:00",
                    "last_updated_at": "2026-03-15T10:00:00",
                },
            ],
            "metadata": {
                "total_count": 2,
                "categories": ["land_acquisition", "contractor_management"],
            },
        }

    @pytest.fixture
    def mock_playbook_detail(self):
        """Mock playbook detail with evidence."""
        return {
            "playbook_id": uuid4(),
            "category": "land_acquisition",
            "label": "Weekly coordination with district administration",
            "confidence_tier": "HIGH",
            "source_project_count": 8,
            "created_at": "2026-03-15T10:00:00",
            "last_updated_at": "2026-03-15T10:00:00",
            "evidence_actions": [
                {
                    "action_id": uuid4(),
                    "action_text": "Weekly direct coordination with district administration",
                    "category": "land_acquisition",
                    "source_month": "2026-03-01",
                    "quote_evidence": "Weekly coordination with district",
                    "specificity_score": 4,
                },
                {
                    "action_id": uuid4(),
                    "action_text": "Regular meetings with district collector",
                    "category": "land_acquisition",
                    "source_month": "2026-02-01",
                    "quote_evidence": "Regular meetings with district collector",
                    "specificity_score": 5,
                },
            ],
        }

    @pytest.fixture
    def mock_suggestions(self):
        """Mock playbook suggestions for a project."""
        return {
            "suggestions": [
                {
                    "suggestion_id": uuid4(),
                    "project_id": uuid4(),
                    "playbook": {
                        "playbook_id": uuid4(),
                        "category": "land_acquisition",
                        "label": "Weekly coordination with district administration",
                        "confidence_tier": "HIGH",
                        "source_project_count": 8,
                    },
                    "triggered_by_risk_category": "MODERATE",
                    "trigger_reason": "Land acquisition delay is a key risk driver",
                    "suggested_at": "2026-03-15T10:00:00",
                    "was_viewed": False,
                    "was_dismissed": False,
                },
            ],
            "metadata": {
                "project_id": uuid4(),
                "total_suggestions": 1,
            },
        }

    def test_get_positive_deviants(self, client, mock_positive_deviants):
        """Test GET /api/v1/positive-deviants endpoint."""
        with patch('app.api.v1.positive_deviance.get_db') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('app.services.positive_deviance.PositiveDevianceDetector.batch_detect') as mock_detect:
                mock_detect.return_value = mock_positive_deviants

                response = client.get("/api/v1/positive-deviants")

                assert response.status_code == 200
                data = response.json()
                assert "positive_deviants" in data
                assert len(data["positive_deviants"]) == 2

    def test_get_positive_deviants_with_filters(self, client, mock_positive_deviants):
        """Test GET /api/v1/positive-deviants with sector filter."""
        with patch('app.api.v1.positive_deviance.get_db') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('app.services.positive_deviance.PositiveDevianceDetector.batch_detect') as mock_detect:
                mock_detect.return_value = mock_positive_deviants

                response = client.get("/api/v1/positive-deviants?sector=Roads")

                assert response.status_code == 200

    def test_get_playbooks(self, client, mock_playbooks):
        """Test GET /api/v1/playbooks endpoint."""
        with patch('app.api.v1.positive_deviance.get_db') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('app.services.playbook_clustering.PlaybookClusterer.get_all_playbooks') as mock_get:
                mock_get.return_value = mock_playbooks

                response = client.get("/api/v1/playbooks")

                assert response.status_code == 200
                data = response.json()
                assert "playbooks" in data
                assert len(data["playbooks"]) == 2

    def test_get_playbooks_with_filters(self, client, mock_playbooks):
        """Test GET /api/v1/playbooks with category filter."""
        with patch('app.api.v1.positive_deviance.get_db') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('app.services.playbook_clustering.PlaybookClusterer.get_all_playbooks') as mock_get:
                mock_get.return_value = mock_playbooks

                response = client.get("/api/v1/playbooks?category=land_acquisition")

                assert response.status_code == 200

    def test_get_playbook_detail(self, client, mock_playbook_detail):
        """Test GET /api/v1/playbooks/{id} endpoint."""
        playbook_id = uuid4()

        with patch('app.api.v1.positive_deviance.get_db') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('app.services.playbook_clustering.PlaybookClusterer.get_playbook_detail') as mock_get:
                mock_get.return_value = mock_playbook_detail

                response = client.get(f"/api/v1/playbooks/{playbook_id}")

                assert response.status_code == 200
                data = response.json()
                assert data["playbook_id"] == mock_playbook_detail["playbook_id"]
                assert "evidence_actions" in data

    def test_get_suggested_playbooks(self, client, mock_suggestions):
        """Test GET /api/v1/projects/{id}/suggested-playbooks endpoint."""
        project_id = uuid4()

        with patch('app.api.v1.positive_deviance.get_db') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('app.services.playbook_matching.PlaybookMatcher.get_suggestions') as mock_get:
                mock_get.return_value = mock_suggestions

                response = client.get(f"/api/v1/projects/{project_id}/suggested-playbooks")

                assert response.status_code == 200
                data = response.json()
                assert "suggestions" in data
                assert len(data["suggestions"]) == 1

    def test_dismiss_suggestion(self, client):
        """Test POST /api/v1/projects/{id}/suggested-playbooks/{suggestion_id}/dismiss endpoint."""
        project_id = uuid4()
        suggestion_id = uuid4()

        with patch('app.api.v1.positive_deviance.get_db') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('app.api.v1.positive_deviance.mark_suggestion_dismissed') as mock_dismiss:
                mock_dismiss.return_value = {"status": "dismissed"}

                response = client.post(
                    f"/api/v1/projects/{project_id}/suggested-playbooks/{suggestion_id}/dismiss"
                )

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "dismissed"

    def test_mark_suggestion_viewed(self, client):
        """Test POST /api/v1/projects/{id}/suggested-playbooks/{suggestion_id}/viewed endpoint."""
        project_id = uuid4()
        suggestion_id = uuid4()

        with patch('app.api.v1.positive_deviance.get_db') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('app.api.v1.positive_deviance.mark_suggestion_viewed') as mock_viewed:
                mock_viewed.return_value = {"status": "viewed"}

                response = client.post(
                    f"/api/v1/projects/{project_id}/suggested-playbooks/{suggestion_id}/viewed"
                )

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "viewed"

    def test_schema_validation(self, client, mock_positive_deviants):
        """Test that API responses match Pydantic schemas."""
        with patch('app.api.v1.positive_deviance.get_db') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('app.services.positive_deviance.PositiveDevianceDetector.batch_detect') as mock_detect:
                mock_detect.return_value = mock_positive_deviants

                response = client.get("/api/v1/positive-deviants")

                assert response.status_code == 200
                data = response.json()
                
                # Validate required fields
                for deviant in data["positive_deviants"]:
                    assert "deviant_id" in deviant
                    assert "project_id" in deviant
                    assert "residual_cost_zscore" in deviant
                    assert "data_confidence_score" in deviant

    def test_empty_response_handling(self, client):
        """Test handling of empty responses."""
        with patch('app.api.v1.positive_deviance.get_db') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('app.services.positive_deviance.PositiveDevianceDetector.batch_detect') as mock_detect:
                mock_detect.return_value = {"positive_deviants": [], "metadata": {"total_count": 0}}

                response = client.get("/api/v1/positive-deviants")

                assert response.status_code == 200
                data = response.json()
                assert data["positive_deviants"] == []

    def test_error_handling(self, client):
        """Test error handling in API endpoints."""
        with patch('app.api.v1.positive_deviance.get_db') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('app.services.positive_deviance.PositiveDevianceDetector.batch_detect') as mock_detect:
                mock_detect.side_effect = Exception("Service unavailable")

                response = client.get("/api/v1/positive-deviants")

                # Should return 500 or appropriate error status
                assert response.status_code in [500, 503]

    def test_anonymization_in_playbook_detail(self, client, mock_playbook_detail):
        """Test that playbook detail does not expose unauthorized project identities."""
        with patch('app.api.v1.positive_deviance.get_db') as mock_db:
            mock_db.return_value = MagicMock()
            with patch('app.services.playbook_clustering.PlaybookClusterer.get_playbook_detail') as mock_get:
                mock_get.return_value = mock_playbook_detail

                response = client.get(f"/api/v1/playbooks/{uuid4()}")

                assert response.status_code == 200
                data = response.json()
                
                # Evidence should not contain project names or IDs
                for action in data.get("evidence_actions", []):
                    assert "project_name" not in action
                    assert "project_id" not in action
