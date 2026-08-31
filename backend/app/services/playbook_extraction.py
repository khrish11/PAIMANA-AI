"""Playbook Extraction service.

Extracts concrete successful practices from narrative reports of positive deviants
using LLM structured output. Reuses the existing Ollama/NID infrastructure.

Allowed categories:
- land_acquisition
- procurement
- contractor_management
- design_change
- stakeholder_coordination
- resource_planning
- other

Only retains actions with specificity_score >= 3.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

import httpx
from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger(__name__)

# Prompt and model versioning
PROMPT_VERSION = "v1"
MODEL_VERSION = "llama3.2"  # Default, can be configured

# Specificity threshold
MIN_SPECIFICITY_SCORE = 3


class ExtractedAction(BaseModel):
    """Structured output for LLM action extraction."""
    action_text: str = Field(description="The concrete action taken")
    category: Literal[
        "land_acquisition",
        "procurement",
        "contractor_management",
        "design_change",
        "stakeholder_coordination",
        "resource_planning",
        "other"
    ] = Field(description="Category of the action")
    source_month: str = Field(description="YYYY-MM of the source narrative")
    quote_evidence: str = Field(description="Direct quote from narrative supporting this action")
    specificity_score: int = Field(description="Specificity score 1-5 (5=most specific)")


class ExtractionResponse(BaseModel):
    """Wrapper for LLM extraction response."""
    actions: list[ExtractedAction] = Field(default_factory=list)


@dataclass(frozen=True)
class ExtractionResult:
    """Result of action extraction for a positive deviant."""
    deviant_id: str
    project_id: str
    actions: list[dict]
    status: Literal["success", "extraction_unavailable", "malformed"]
    model_version: str
    prompt_version: str
    error_message: str | None
    extracted_at: datetime


def _build_extraction_prompt(narrative_text: str, source_month: str) -> str:
    """Build the prompt for LLM action extraction.
    
    Args:
        narrative_text: The narrative text to extract actions from
        source_month: The source month in YYYY-MM format
    
    Returns:
        The complete prompt for the LLM
    """
    return f"""Extract concrete, specific actions taken by the project team from the following narrative report.

Focus ONLY on actions that contributed to positive outcomes (e.g., resolving delays, cost savings, stakeholder alignment).

For each action, provide:
- action_text: A concise description of what was done
- category: One of: land_acquisition, procurement, contractor_management, design_change, stakeholder_coordination, resource_planning, other
- source_month: "{source_month}"
- quote_evidence: A direct quote from the narrative that supports this action
- specificity_score: 1-5 (5=very specific with clear details, 1=vague/generic)

Only include actions with specificity_score >= 3. If no specific actions are found, return an empty list.

Narrative text:
{narrative_text}

Return the result in the following JSON format:
{{
  "actions": [
    {{
      "action_text": "...",
      "category": "...",
      "source_month": "{source_month}",
      "quote_evidence": "...",
      "specificity_score": 3
    }}
  ]
}}"""


async def _call_ollama_extraction(prompt: str) -> dict | None:
    """Call Ollama LLM for structured extraction.
    
    Args:
        prompt: The prompt to send to the LLM
    
    Returns:
        Parsed JSON response or None on failure
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": MODEL_VERSION,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
            )
            response.raise_for_status()
            result = response.json()
            
            # Parse the response
            if "response" in result:
                import json
                return json.loads(result["response"])
            
            return result
    except Exception as exc:
        logger.error("Ollama extraction failed: %s", exc)
        return None


def _filter_by_specificity(actions: list[dict]) -> list[dict]:
    """Filter actions by specificity score threshold.
    
    Args:
        actions: List of action dictionaries
    
    Returns:
        Filtered list with specificity_score >= MIN_SPECIFICITY_SCORE
    """
    return [a for a in actions if a.get("specificity_score", 0) >= MIN_SPECIFICITY_SCORE]


async def extract_actions_from_narrative(
    deviant_id: str,
    project_id: str,
    narrative_text: str,
    source_month: str,
) -> ExtractionResult:
    """Extract concrete actions from narrative text for a positive deviant.
    
    Args:
        deviant_id: The positive deviant ID
        project_id: The project ID
        narrative_text: The narrative text to extract from
        source_month: The source month in YYYY-MM format
    
    Returns:
        ExtractionResult with extracted actions or error status
    """
    if not narrative_text or not narrative_text.strip():
        return ExtractionResult(
            deviant_id=deviant_id,
            project_id=project_id,
            actions=[],
            status="extraction_unavailable",
            model_version=MODEL_VERSION,
            prompt_version=PROMPT_VERSION,
            error_message="Empty narrative text",
            extracted_at=datetime.utcnow(),
        )
    
    # Build prompt
    prompt = _build_extraction_prompt(narrative_text, source_month)
    
    # Call LLM
    llm_response = await _call_ollama_extraction(prompt)
    
    if llm_response is None:
        logger.warning(
            "LLM extraction unavailable for deviant %s (project %s)",
            deviant_id, project_id
        )
        return ExtractionResult(
            deviant_id=deviant_id,
            project_id=project_id,
            actions=[],
            status="extraction_unavailable",
            model_version=MODEL_VERSION,
            prompt_version=PROMPT_VERSION,
            error_message="LLM service unavailable",
            extracted_at=datetime.utcnow(),
        )
    
    # Parse response
    try:
        if isinstance(llm_response, dict) and "actions" in llm_response:
            actions = llm_response["actions"]
        else:
            logger.error(
                "Malformed LLM response for deviant %s (project %s): %s",
                deviant_id, project_id, llm_response
            )
            return ExtractionResult(
                deviant_id=deviant_id,
                project_id=project_id,
                actions=[],
                status="malformed",
                model_version=MODEL_VERSION,
                prompt_version=PROMPT_VERSION,
                error_message="Malformed LLM response structure",
                extracted_at=datetime.utcnow(),
            )
        
        # Validate and filter actions
        filtered_actions = _filter_by_specificity(actions)
        
        logger.info(
            "Extracted %d actions for deviant %s (project %s) from %d total",
            len(filtered_actions), deviant_id, project_id, len(actions)
        )
        
        # Log raw output for audit trail
        logger.debug(
            "Raw LLM output for deviant %s (project %s): %s",
            deviant_id, project_id, llm_response
        )
        
        return ExtractionResult(
            deviant_id=deviant_id,
            project_id=project_id,
            actions=filtered_actions,
            status="success",
            model_version=MODEL_VERSION,
            prompt_version=PROMPT_VERSION,
            error_message=None,
            extracted_at=datetime.utcnow(),
        )
        
    except Exception as exc:
        logger.error(
            "Failed to parse extraction response for deviant %s (project %s): %s",
            deviant_id, project_id, exc
        )
        return ExtractionResult(
            deviant_id=deviant_id,
            project_id=project_id,
            actions=[],
            status="malformed",
            model_version=MODEL_VERSION,
            prompt_version=PROMPT_VERSION,
            error_message=str(exc),
            extracted_at=datetime.utcnow(),
        )


class PlaybookExtractor:
    """Compatibility wrapper for LLM-driven action extraction."""

    def __init__(self, llm_model_version: str = MODEL_VERSION, prompt_version: str = PROMPT_VERSION):
        self.llm_model_version = llm_model_version
        self.prompt_version = prompt_version

    async def _call_ollama(self, prompt: str) -> dict | None:
        return await _call_ollama_extraction(prompt)

    def _construct_prompt(self, deviant: dict) -> str:
        narrative_text = deviant.get("narrative_text", "")
        source_month = deviant.get("reporting_month") or "2026-01-01"
        return _build_extraction_prompt(narrative_text, str(source_month))

    async def extract_actions(self, deviant: dict) -> list[dict]:
        if not deviant or not deviant.get("narrative_text"):
            return []

        llm_response = await self._call_ollama(self._construct_prompt(deviant))
        if llm_response is None:
            return []

        if not isinstance(llm_response, dict) or "actions" not in llm_response:
            return []

        actions = llm_response["actions"]
        filtered_actions = _filter_by_specificity(actions)

        for action in filtered_actions:
            action.setdefault("llm_model_version", self.llm_model_version)
            action.setdefault("prompt_version", self.prompt_version)
        return filtered_actions


async def extract_actions_from_multiple_months(
    deviant_id: str,
    project_id: str,
    narratives_by_month: dict[str, str],
) -> ExtractionResult:
    """Extract actions from multiple months of narrative text.
    
    Args:
        deviant_id: The positive deviant ID
        project_id: The project ID
        narratives_by_month: Dict mapping YYYY-MM to narrative text
    
    Returns:
        Combined ExtractionResult with all extracted actions
    """
    all_actions = []
    errors = []
    
    for month, narrative in sorted(narratives_by_month.items()):
        try:
            result = await extract_actions_from_narrative(
                deviant_id, project_id, narrative, month
            )
            
            if result.status == "success":
                all_actions.extend(result.actions)
            else:
                errors.append(f"{month}: {result.error_message}")
                
        except Exception as exc:
            errors.append(f"{month}: {str(exc)}")
    
    # Combine results
    combined_status = "success" if all_actions else ("extraction_unavailable" if not errors else "malformed")
    combined_error = "; ".join(errors) if errors else None
    
    logger.info(
        "Extracted %d total actions from %d months for deviant %s (project %s)",
        len(all_actions), len(narratives_by_month), deviant_id, project_id
    )
    
    return ExtractionResult(
        deviant_id=deviant_id,
        project_id=project_id,
        actions=all_actions,
        status=combined_status,
        model_version=MODEL_VERSION,
        prompt_version=PROMPT_VERSION,
        error_message=combined_error,
        extracted_at=datetime.utcnow(),
    )
