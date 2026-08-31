import pytest
from uuid import uuid4
from datetime import date

from app.services.playbook_matching import PlaybookMatcher


@pytest.mark.db
class TestPlaybookMatcher:
    """Test playbook matching to struggling projects."""

    @pytest.fixture
    def matcher(self):
        return PlaybookMatcher()

    @pytest.fixture
    def mock_struggling_project(self):
        """Mock struggling project with MODERATE risk."""
        return {
            "project_id": uuid4(),
            "project_name": "Struggling Highway Project",
            "sector": "Roads",
            "state": "Uttar Pradesh",
            "composite_score": 65,
            "risk_category": "MODERATE",
            "shap_drivers": [
                {
                    "feature": "land_related_delay",
                    "human_label": "Land Acquisition Delay",
                    "contribution": 0.3,
                    "direction": "increases_risk",
                },
                {
                    "feature": "contractor_performance",
                    "human_label": "Contractor Performance",
                    "contribution": 0.2,
                    "direction": "increases_risk",
                },
            ],
            "reference_class_id": uuid4(),
            "pbe_profile": {"sector": "Roads", "size_band": "Large"},
        }

    @pytest.fixture
    def mock_high_risk_project(self):
        """Mock struggling project with HIGH risk."""
        return {
            "project_id": uuid4(),
            "project_name": "High Risk Project",
            "sector": "Roads",
            "state": "Bihar",
            "composite_score": 85,
            "risk_category": "HIGH",
            "shap_drivers": [
                {
                    "feature": "land_related_delay",
                    "human_label": "Land Acquisition Delay",
                    "contribution": 0.4,
                    "direction": "increases_risk",
                },
            ],
            "reference_class_id": uuid4(),
            "pbe_profile": {"sector": "Roads", "size_band": "Large"},
        }

    @pytest.fixture
    def mock_low_risk_project(self):
        """Mock project with LOW risk (should not trigger matching)."""
        return {
            "project_id": uuid4(),
            "project_name": "Low Risk Project",
            "sector": "Roads",
            "state": "Gujarat",
            "composite_score": 25,
            "risk_category": "LOW",
            "shap_drivers": [],
            "reference_class_id": uuid4(),
            "pbe_profile": {"sector": "Roads", "size_band": "Large"},
        }

    @pytest.fixture
    def mock_playbooks(self):
        """Mock available playbooks."""
        return [
            {
                "playbook_id": uuid4(),
                "category": "land_acquisition",
                "label": "Weekly coordination with district administration",
                "confidence_tier": "HIGH",
                "source_project_count": 8,
                "source_action_ids": [uuid4(), uuid4(), uuid4()],
                "reference_class_compatibility": ["Roads", "Large"],
            },
            {
                "playbook_id": uuid4(),
                "category": "contractor_management",
                "label": "Regular contractor performance reviews",
                "confidence_tier": "MEDIUM",
                "source_project_count": 5,
                "source_action_ids": [uuid4(), uuid4(), uuid4()],
                "reference_class_compatibility": ["Roads", "Medium"],
            },
            {
                "playbook_id": uuid4(),
                "category": "land_acquisition",
                "label": "Direct district collector involvement",
                "confidence_tier": "LOW",
                "source_project_count": 3,
                "source_action_ids": [uuid4(), uuid4(), uuid4()],
                "reference_class_compatibility": ["Roads", "Large"],
            },
        ]

    def test_moderate_risk_trigger(self, matcher, mock_struggling_project, mock_playbooks):
        """Test that MODERATE risk triggers matching."""
        suggestions = matcher.match_playbooks(mock_struggling_project, mock_playbooks)
        
        assert len(suggestions) > 0

    def test_high_risk_trigger(self, matcher, mock_high_risk_project, mock_playbooks):
        """Test that HIGH risk triggers matching."""
        suggestions = matcher.match_playbooks(mock_high_risk_project, mock_playbooks)
        
        assert len(suggestions) > 0

    def test_low_risk_no_trigger(self, matcher, mock_low_risk_project, mock_playbooks):
        """Test that LOW risk does not trigger matching."""
        suggestions = matcher.match_playbooks(mock_low_risk_project, mock_playbooks)
        
        assert len(suggestions) == 0

    def test_category_matching(self, matcher, mock_struggling_project, mock_playbooks):
        """Test that playbooks match based on SHAP category."""
        suggestions = matcher.match_playbooks(mock_struggling_project, mock_playbooks)
        
        # Should prefer land_acquisition playbooks due to land_related_delay driver
        land_playbooks = [s for s in suggestions if s["playbook"]["category"] == "land_acquisition"]
        assert len(land_playbooks) > 0

    def test_confidence_tier_priority(self, matcher, mock_struggling_project, mock_playbooks):
        """Test that HIGH/MEDIUM confidence playbooks are prioritized."""
        suggestions = matcher.match_playbooks(mock_struggling_project, mock_playbooks)
        
        # Should prioritize HIGH and MEDIUM over LOW
        high_medium_suggestions = [
            s for s in suggestions 
            if s["playbook"]["confidence_tier"] in ["HIGH", "MEDIUM"]
        ]
        assert len(high_medium_suggestions) > 0

    def test_top_1_3_selection(self, matcher, mock_struggling_project, mock_playbooks):
        """Test that only top 1-3 suggestions are returned."""
        suggestions = matcher.match_playbooks(mock_struggling_project, mock_playbooks)
        
        assert len(suggestions) <= 3
        assert len(suggestions) >= 1

    def test_source_project_similarity(self, matcher, mock_struggling_project):
        """Test that source project count is considered in ranking."""
        playbooks = [
            {
                "playbook_id": uuid4(),
                "category": "land_acquisition",
                "label": "High evidence playbook",
                "confidence_tier": "HIGH",
                "source_project_count": 10,
                "source_action_ids": [uuid4(), uuid4(), uuid4()],
                "reference_class_compatibility": ["Roads", "Large"],
            },
            {
                "playbook_id": uuid4(),
                "category": "land_acquisition",
                "label": "Low evidence playbook",
                "confidence_tier": "HIGH",
                "source_project_count": 3,
                "source_action_ids": [uuid4(), uuid4(), uuid4()],
                "reference_class_compatibility": ["Roads", "Large"],
            },
        ]
        
        suggestions = matcher.match_playbooks(mock_struggling_project, playbooks)
        
        # Higher source project count should rank higher
        assert suggestions[0]["playbook"]["source_project_count"] >= suggestions[-1]["playbook"]["source_project_count"]

    def test_reference_class_compatibility(self, matcher, mock_struggling_project):
        """Test that reference class compatibility is considered."""
        playbooks = [
            {
                "playbook_id": uuid4(),
                "category": "land_acquisition",
                "label": "Compatible playbook",
                "confidence_tier": "HIGH",
                "source_project_count": 5,
                "source_action_ids": [uuid4(), uuid4(), uuid4()],
                "reference_class_compatibility": ["Roads", "Large"],  # Compatible
            },
            {
                "playbook_id": uuid4(),
                "category": "land_acquisition",
                "label": "Incompatible playbook",
                "confidence_tier": "HIGH",
                "source_project_count": 5,
                "source_action_ids": [uuid4(), uuid4(), uuid4()],
                "reference_class_compatibility": ["Railways", "Large"],  # Incompatible
            },
        ]
        
        suggestions = matcher.match_playbooks(mock_struggling_project, playbooks)
        
        # Compatible playbook should be ranked higher
        assert "Roads" in suggestions[0]["playbook"]["reference_class_compatibility"]

    def test_shap_feature_mapping(self, matcher):
        """Test SHAP feature to category mapping."""
        shap_feature = "land_related_delay"
        category = matcher._map_shap_feature_to_category(shap_feature)
        
        assert category == "land_acquisition"

    def test_shap_feature_mapping_contractor(self, matcher):
        """Test SHAP feature mapping for contractor."""
        shap_feature = "contractor_performance"
        category = matcher._map_shap_feature_to_category(shap_feature)
        
        assert category == "contractor_management"

    def test_shap_feature_mapping_unknown(self, matcher):
        """Test SHAP feature mapping for unknown feature."""
        shap_feature = "unknown_feature"
        category = matcher._map_shap_feature_to_category(shap_feature)
        
        assert category is None

    def test_relevance_scoring(self, matcher, mock_struggling_project, mock_playbooks):
        """Test relevance scoring of suggestions."""
        suggestions = matcher.match_playbooks(mock_struggling_project, mock_playbooks)
        
        # All suggestions should have relevance scores
        for suggestion in suggestions:
            assert "relevance_score" in suggestion
            assert 0 <= suggestion["relevance_score"] <= 1

    def test_trigger_reason_generation(self, matcher, mock_struggling_project, mock_playbooks):
        """Test that trigger reason is generated."""
        suggestions = matcher.match_playbooks(mock_struggling_project, mock_playbooks)
        
        # Suggestions should include trigger reason
        for suggestion in suggestions:
            assert "trigger_reason" in suggestion
            assert len(suggestion["trigger_reason"]) > 0

    def test_empty_playbooks(self, matcher, mock_struggling_project):
        """Test handling of empty playbook list."""
        suggestions = matcher.match_playbooks(mock_struggling_project, [])
        
        assert len(suggestions) == 0

    def test_no_matching_category(self, matcher, mock_struggling_project):
        """Test when no playbooks match the SHAP category."""
        playbooks = [
            {
                "playbook_id": uuid4(),
                "category": "procurement",  # Different category
                "label": "Procurement improvement",
                "confidence_tier": "HIGH",
                "source_project_count": 5,
                "source_action_ids": [uuid4(), uuid4(), uuid4()],
                "reference_class_compatibility": ["Roads", "Large"],
            },
        ]
        
        suggestions = matcher.match_playbooks(mock_struggling_project, playbooks)
        
        # Should return empty or low-relevance suggestions
        assert len(suggestions) == 0 or all(s["relevance_score"] < 0.3 for s in suggestions)
