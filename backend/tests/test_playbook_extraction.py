import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from app.services.playbook_extraction import PlaybookExtractor


@pytest.mark.db
class TestPlaybookExtractor:
    """Test playbook extraction from narratives."""

    @pytest.fixture
    def extractor(self):
        return PlaybookExtractor()

    @pytest.fixture
    def mock_deviant(self):
        """Mock positive deviant with narrative data."""
        return {
            "deviant_id": uuid4(),
            "project_id": uuid4(),
            "project_name": "Test Highway Project",
            "reporting_month": "2026-03-01",
            "narrative_text": """
            We implemented weekly direct coordination with district administration,
            which significantly reduced land acquisition delays. The district
            collector was personally involved in resolving disputes. This approach
            helped us acquire 85% of required land within 6 months.
            """,
        }

    @pytest.fixture
    def valid_llm_response(self):
        """Mock valid LLM response with structured actions."""
        return {
            "actions": [
                {
                    "action_text": "Weekly direct coordination with district administration",
                    "category": "land_acquisition",
                    "source_month": "2026-03-01",
                    "quote_evidence": "We implemented weekly direct coordination with district administration",
                    "specificity_score": 4,
                },
                {
                    "action_text": "District collector involvement in dispute resolution",
                    "category": "land_acquisition",
                    "source_month": "2026-03-01",
                    "quote_evidence": "The district collector was personally involved in resolving disputes",
                    "specificity_score": 5,
                },
            ]
        }

    @pytest.fixture
    def malformed_llm_response(self):
        """Mock malformed LLM response."""
        return {
            "invalid_field": "This is not a valid response",
            "actions": "not a list",
        }

    @pytest.fixture
    def low_specificity_response(self):
        """Mock LLM response with low specificity scores."""
        return {
            "actions": [
                {
                    "action_text": "Good coordination",
                    "category": "land_acquisition",
                    "source_month": "2026-03-01",
                    "quote_evidence": "We had good coordination",
                    "specificity_score": 2,  # Below MIN_SPECIFICITY_SCORE
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_valid_extraction(self, extractor, mock_deviant, valid_llm_response):
        """Test successful extraction with valid LLM response."""
        with patch.object(extractor, '_call_ollama', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.return_value = valid_llm_response

            actions = await extractor.extract_actions(mock_deviant)

            assert len(actions) == 2
            assert actions[0]["action_text"] == "Weekly direct coordination with district administration"
            assert actions[0]["category"] == "land_acquisition"
            assert actions[0]["specificity_score"] == 4
            assert actions[1]["specificity_score"] == 5

    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, extractor, mock_deviant, malformed_llm_response):
        """Test handling of malformed LLM response."""
        with patch.object(extractor, '_call_ollama', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.return_value = malformed_llm_response

            actions = await extractor.extract_actions(mock_deviant)

            # Should return empty list and log error
            assert len(actions) == 0

    @pytest.mark.asyncio
    async def test_empty_extraction(self, extractor, mock_deviant):
        """Test handling of empty LLM response."""
        with patch.object(extractor, '_call_ollama', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.return_value = {"actions": []}

            actions = await extractor.extract_actions(mock_deviant)

            assert len(actions) == 0

    @pytest.mark.asyncio
    async def test_specificity_filtering(self, extractor, mock_deviant, low_specificity_response):
        """Test filtering of low specificity actions."""
        with patch.object(extractor, '_call_ollama', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.return_value = low_specificity_response

            actions = await extractor.extract_actions(mock_deviant)

            # Should filter out actions with specificity < 3
            assert len(actions) == 0

    def test_prompt_construction(self, extractor, mock_deviant):
        """Test LLM prompt construction."""
        prompt = extractor._construct_prompt(mock_deviant)

        assert "narrative" in prompt.lower()
        assert mock_deviant["narrative_text"] in prompt
        assert "action_text" in prompt
        assert "category" in prompt
        assert "specificity_score" in prompt

    def test_model_version_logging(self, extractor, mock_deviant, valid_llm_response):
        """Test that model version is logged."""
        extractor.llm_model_version = "llama3.2"
        extractor.prompt_version = "v1"

        # The model version should be included in the extracted action metadata
        assert extractor.llm_model_version == "llama3.2"
        assert extractor.prompt_version == "v1"

    @pytest.mark.asyncio
    async def test_ollama_failure_handling(self, extractor, mock_deviant):
        """Test handling of Ollama service failure."""
        with patch.object(extractor, '_call_ollama', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.side_effect = Exception("Ollama service unavailable")

            actions = await extractor.extract_actions(mock_deviant)

            # Should return empty list on failure
            assert len(actions) == 0

    @pytest.mark.asyncio
    async def test_mixed_specificity_filtering(self, extractor, mock_deviant):
        """Test filtering with mixed specificity scores."""
        mixed_response = {
            "actions": [
                {
                    "action_text": "Weekly coordination",
                    "category": "land_acquisition",
                    "source_month": "2026-03-01",
                    "quote_evidence": "Weekly coordination",
                    "specificity_score": 2,  # Should be filtered
                },
                {
                    "action_text": "Weekly direct coordination with district administration",
                    "category": "land_acquisition",
                    "source_month": "2026-03-01",
                    "quote_evidence": "Weekly direct coordination",
                    "specificity_score": 4,  # Should be kept
                },
                {
                    "action_text": "Good work",
                    "category": "land_acquisition",
                    "source_month": "2026-03-01",
                    "quote_evidence": "Good work",
                    "specificity_score": 1,  # Should be filtered
                },
            ]
        }

        with patch.object(extractor, '_call_ollama', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.return_value = mixed_response

            actions = await extractor.extract_actions(mock_deviant)

            # Only the action with specificity >= 3 should remain
            assert len(actions) == 1
            assert actions[0]["specificity_score"] == 4
