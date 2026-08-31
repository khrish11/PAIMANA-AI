import pytest
from uuid import uuid4
from datetime import datetime

from app.services.playbook_clustering import PlaybookClusterer


@pytest.mark.db
class TestPlaybookClusterer:
    """Test playbook clustering logic."""

    @pytest.fixture
    def clusterer(self):
        return PlaybookClusterer()

    @pytest.fixture
    def actions_from_3_projects(self):
        """Mock actions from 3 different projects (same category)."""
        project_a_id = uuid4()
        project_b_id = uuid4()
        project_c_id = uuid4()

        return [
            {
                "action_id": uuid4(),
                "deviant_id": uuid4(),
                "project_id": project_a_id,
                "action_text": "Weekly direct coordination with district administration",
                "category": "land_acquisition",
                "source_month": "2026-03-01",
                "quote_evidence": "Weekly coordination with district",
                "specificity_score": 4,
            },
            {
                "action_id": uuid4(),
                "deviant_id": uuid4(),
                "project_id": project_b_id,
                "action_text": "Regular meetings with district collector",
                "category": "land_acquisition",
                "source_month": "2026-02-01",
                "quote_evidence": "Regular meetings with district collector",
                "specificity_score": 4,
            },
            {
                "action_id": uuid4(),
                "deviant_id": uuid4(),
                "project_id": project_c_id,
                "action_text": "Direct coordination with district administration",
                "category": "land_acquisition",
                "source_month": "2026-01-01",
                "quote_evidence": "Direct coordination with district",
                "specificity_score": 5,
            },
        ]

    @pytest.fixture
    def actions_from_1_project(self):
        """Mock actions from only 1 project (should be rejected)."""
        project_id = uuid4()

        return [
            {
                "action_id": uuid4(),
                "deviant_id": uuid4(),
                "project_id": project_id,
                "action_text": "Weekly coordination with district",
                "category": "land_acquisition",
                "source_month": "2026-03-01",
                "quote_evidence": "Weekly coordination",
                "specificity_score": 4,
            },
            {
                "action_id": uuid4(),
                "deviant_id": uuid4(),
                "project_id": project_id,
                "action_text": "Regular meetings with district collector",
                "category": "land_acquisition",
                "source_month": "2026-02-01",
                "quote_evidence": "Regular meetings",
                "specificity_score": 4,
            },
            {
                "action_id": uuid4(),
                "deviant_id": uuid4(),
                "project_id": project_id,
                "action_text": "Direct coordination with district",
                "category": "land_acquisition",
                "source_month": "2026-01-01",
                "quote_evidence": "Direct coordination",
                "specificity_score": 5,
            },
        ]

    @pytest.fixture
    def actions_from_2_projects(self):
        """Mock actions from 2 projects (should be rejected)."""
        project_a_id = uuid4()
        project_b_id = uuid4()

        return [
            {
                "action_id": uuid4(),
                "deviant_id": uuid4(),
                "project_id": project_a_id,
                "action_text": "Weekly coordination with district",
                "category": "land_acquisition",
                "source_month": "2026-03-01",
                "quote_evidence": "Weekly coordination",
                "specificity_score": 4,
            },
            {
                "action_id": uuid4(),
                "deviant_id": uuid4(),
                "project_id": project_b_id,
                "action_text": "Regular meetings with district collector",
                "category": "land_acquisition",
                "source_month": "2026-02-01",
                "quote_evidence": "Regular meetings",
                "specificity_score": 4,
            },
        ]

    @pytest.fixture
    def actions_from_7_projects(self):
        """Mock actions from 7 projects (should get HIGH confidence)."""
        actions = []
        for i in range(7):
            project_id = uuid4()
            actions.append({
                "action_id": uuid4(),
                "deviant_id": uuid4(),
                "project_id": project_id,
                "action_text": f"Coordination with district administration {i}",
                "category": "land_acquisition",
                "source_month": f"2026-{i+1:02d}-01",
                "quote_evidence": f"Coordination {i}",
                "specificity_score": 4,
            })
        return actions

    def test_singleton_rejection(self, clusterer, actions_from_1_project):
        """Test that single-project clusters are rejected."""
        playbooks = clusterer.cluster_actions(actions_from_1_project, "land_acquisition")
        
        assert len(playbooks) == 0

    def test_2_project_rejection(self, clusterer, actions_from_2_projects):
        """Test that 2-project clusters are rejected."""
        playbooks = clusterer.cluster_actions(actions_from_2_projects, "land_acquisition")
        
        assert len(playbooks) == 0

    def test_3_project_acceptance(self, clusterer, actions_from_3_projects):
        """Test that 3-project clusters are accepted."""
        playbooks = clusterer.cluster_actions(actions_from_3_projects, "land_acquisition")
        
        assert len(playbooks) == 1
        playbook = playbooks[0]
        assert playbook["confidence_tier"] == "LOW"
        assert playbook["source_project_count"] == 3

    def test_confidence_tier_low(self, clusterer, actions_from_3_projects):
        """Test LOW confidence tier (3 projects)."""
        playbooks = clusterer.cluster_actions(actions_from_3_projects, "land_acquisition")
        
        assert playbooks[0]["confidence_tier"] == "LOW"

    def test_confidence_tier_medium(self, clusterer):
        """Test MEDIUM confidence tier (4-6 projects)."""
        actions = []
        for i in range(5):
            project_id = uuid4()
            actions.append({
                "action_id": uuid4(),
                "deviant_id": uuid4(),
                "project_id": project_id,
                "action_text": f"Coordination with district {i}",
                "category": "land_acquisition",
                "source_month": f"2026-{i+1:02d}-01",
                "quote_evidence": f"Coordination {i}",
                "specificity_score": 4,
            })
        
        playbooks = clusterer.cluster_actions(actions, "land_acquisition")
        
        assert playbooks[0]["confidence_tier"] == "MEDIUM"

    def test_confidence_tier_high(self, clusterer, actions_from_7_projects):
        """Test HIGH confidence tier (7+ projects)."""
        playbooks = clusterer.cluster_actions(actions_from_7_projects, "land_acquisition")
        
        assert playbooks[0]["confidence_tier"] == "HIGH"

    def test_independent_project_counting(self, clusterer, actions_from_3_projects):
        """Test that independent projects are counted correctly."""
        playbooks = clusterer.cluster_actions(actions_from_3_projects, "land_acquisition")
        
        # Should count unique project IDs, not total actions
        assert playbooks[0]["source_project_count"] == 3

    def test_repeated_action_grouping(self, clusterer):
        """Test that similar actions from same project are grouped correctly."""
        project_id = uuid4()
        
        actions = [
            {
                "action_id": uuid4(),
                "deviant_id": uuid4(),
                "project_id": project_id,
                "action_text": "Weekly coordination with district",
                "category": "land_acquisition",
                "source_month": "2026-03-01",
                "quote_evidence": "Weekly coordination",
                "specificity_score": 4,
            },
            {
                "action_id": uuid4(),
                "deviant_id": uuid4(),
                "project_id": uuid4(),  # Different project
                "action_text": "Weekly coordination with district",
                "category": "land_acquisition",
                "source_month": "2026-02-01",
                "quote_evidence": "Weekly coordination",
                "specificity_score": 4,
            },
            {
                "action_id": uuid4(),
                "deviant_id": uuid4(),
                "project_id": uuid4(),  # Third project
                "action_text": "Weekly coordination with district",
                "category": "land_acquisition",
                "source_month": "2026-01-01",
                "quote_evidence": "Weekly coordination",
                "specificity_score": 4,
            },
        ]
        
        playbooks = clusterer.cluster_actions(actions, "land_acquisition")
        
        # Should create one playbook with 3 independent projects
        assert len(playbooks) == 1
        assert playbooks[0]["source_project_count"] == 3

    def test_category_filtering(self, clusterer, actions_from_3_projects):
        """Test that actions are filtered by category."""
        # Add actions from different category
        actions_from_3_projects.append({
            "action_id": uuid4(),
            "deviant_id": uuid4(),
            "project_id": uuid4(),
            "action_text": "Procurement process improvement",
            "category": "procurement",  # Different category
            "source_month": "2026-03-01",
            "quote_evidence": "Procurement improvement",
            "specificity_score": 4,
        })
        
        playbooks = clusterer.cluster_actions(actions_from_3_projects, "land_acquisition")
        
        # Should only cluster land_acquisition actions
        assert len(playbooks) == 1
        assert playbooks[0]["category"] == "land_acquisition"

    def test_empty_actions(self, clusterer):
        """Test handling of empty action list."""
        playbooks = clusterer.cluster_actions([], "land_acquisition")
        
        assert len(playbooks) == 0

    def test_playbook_label_generation(self, clusterer, actions_from_3_projects):
        """Test that playbook label is generated from actions."""
        playbooks = clusterer.cluster_actions(actions_from_3_projects, "land_acquisition")
        
        assert playbooks[0]["label"] is not None
        assert len(playbooks[0]["label"]) > 0
