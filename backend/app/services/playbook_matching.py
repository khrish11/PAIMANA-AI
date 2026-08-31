"""Playbook Matching service.

Matches playbooks to struggling projects based on risk triggers, SHAP drivers,
reference class compatibility, and PBE profile similarity.

Triggered when composite risk >= MODERATE.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from app.services.risk_scoring import RiskCategory

logger = logging.getLogger(__name__)

# Risk threshold for triggering playbook suggestions
RISK_TRIGGER_THRESHOLD = RiskCategory.MODERATE

# SHAP feature to playbook category mapping
SHAP_TO_CATEGORY_MAP = {
    # Land-related features
    "land_acquisition_delay": "land_acquisition",
    "land_acquisition_cost": "land_acquisition",
    "land_clearance": "land_acquisition",
    "land_related_delay": "land_acquisition",
    "land_related_cost": "land_acquisition",

    # Contractor-related features
    "contractor_performance": "contractor_management",
    "contractor_change": "contractor_management",
    "contractor_delay": "contractor_management",

    # Schedule/resource features
    "schedule_variance": "resource_planning",
    "resource_allocation": "resource_planning",
    "manpower_planning": "resource_planning",

    # Procurement features
    "procurement_delay": "procurement",
    "procurement_cost": "procurement",

    # Design features
    "design_change_count": "design_change",
    "design_revision": "design_change",

    # Stakeholder features
    "stakeholder_issues": "stakeholder_coordination",
    "coordination_delay": "stakeholder_coordination",
}


@dataclass(frozen=True)
class PlaybookMatch:
    """A matched playbook for a project."""
    playbook_id: str
    playbook_label: str
    category: str
    confidence_tier: Literal["LOW", "MEDIUM", "HIGH"]
    source_project_count: int
    relevance_score: float
    trigger_reason: str


def map_shap_to_category(shap_feature: str) -> str | None:
    """Map a SHAP feature name to a playbook category.
    
    Args:
        shap_feature: SHAP feature name
    
    Returns:
        Playbook category or None if no mapping exists
    """
    # Direct mapping
    if shap_feature in SHAP_TO_CATEGORY_MAP:
        return SHAP_TO_CATEGORY_MAP[shap_feature]
    
    # Fuzzy matching for partial matches
    for feature, category in SHAP_TO_CATEGORY_MAP.items():
        if feature in shap_feature or shap_feature in feature:
            return category
    
    return None


def calculate_relevance_score(
    playbook_category: str,
    shap_categories: list[str],
    reference_class_match: bool,
    profile_similarity: float,
    source_project_count: int,
) -> float:
    """Calculate relevance score for a playbook match.
    
    Args:
        playbook_category: The playbook's category
        shap_categories: List of SHAP-derived categories from risk drivers
        reference_class_match: Whether playbook matches project's reference class
        profile_similarity: PBE profile similarity score (0-1)
        source_project_count: Number of source projects for the playbook
    
    Returns:
        Relevance score (0-1)
    """
    score = 0.0
    
    # Category relevance (40% weight)
    if playbook_category in shap_categories:
        score += 0.4
    
    # Reference class compatibility (20% weight)
    if reference_class_match:
        score += 0.2
    
    # Profile similarity (20% weight)
    score += profile_similarity * 0.2
    
    # Source project count (20% weight, capped at 10 projects)
    project_score = min(source_project_count / 10.0, 1.0)
    score += project_score * 0.2
    
    return min(score, 1.0)


def match_playbooks_for_project(
    project_id: str,
    composite_risk_score: float,
    risk_category: RiskCategory,
    shap_drivers: list[dict],
    reference_class_id: str | None,
    pbe_profile_similarity: float,
    available_playbooks: list[dict],
) -> list[PlaybookMatch]:
    """Match playbooks to a struggling project.
    
    Args:
        project_id: The project ID
        composite_risk_score: Composite risk score
        risk_category: Risk category
        shap_drivers: List of SHAP driver dicts with feature_name and contribution
        reference_class_id: Project's reference class ID
        pbe_profile_similarity: PBE profile similarity score
        available_playbooks: List of available playbook dicts with:
            - playbook_id
            - category
            - label
            - confidence_tier
            - source_project_count
            - source_reference_classes (optional)
    
    Returns:
        List of matched playbooks ranked by relevance, top 1-3
    """
    # Check if risk trigger is met
    if risk_category not in [RiskCategory.MODERATE, RiskCategory.HIGH, RiskCategory.VERY_HIGH, RiskCategory.CRITICAL]:
        logger.debug(
            "Project %s not eligible for playbook matching: risk category %s",
            project_id, risk_category
        )
        return []
    
    # Extract SHAP-derived categories
    shap_categories = []
    for driver in shap_drivers:
        feature_name = driver.get("feature_name", "")
        category = map_shap_to_category(feature_name)
        if category:
            shap_categories.append(category)
    
    if not shap_categories:
        logger.debug(
            "Project %s: no relevant SHAP categories found for playbook matching",
            project_id
        )
        return []
    
    # Filter playbooks by confidence tier (MEDIUM and HIGH first)
    high_confidence_playbooks = [
        p for p in available_playbooks 
        if p.get("confidence_tier") in ["MEDIUM", "HIGH"]
    ]
    
    # If no MEDIUM/HIGH playbooks, consider LOW
    if not high_confidence_playbooks:
        high_confidence_playbooks = available_playbooks
    
    # Score and rank playbooks
    matches = []
    
    for playbook in high_confidence_playbooks:
        playbook_category = playbook.get("category", "other")
        
        # Check category relevance
        if playbook_category not in shap_categories:
            continue
        
        # Calculate reference class match (simplified)
        reference_class_match = False
        playbook_ref_classes = playbook.get("source_reference_classes", [])
        if reference_class_id and reference_class_id in playbook_ref_classes:
            reference_class_match = True
        
        # Calculate relevance score
        relevance = calculate_relevance_score(
            playbook_category=playbook_category,
            shap_categories=shap_categories,
            reference_class_match=reference_class_match,
            profile_similarity=pbe_profile_similarity,
            source_project_count=playbook.get("source_project_count", 0),
        )
        
        # Determine trigger reason
        trigger_reason = f"Risk category {risk_category} with {playbook_category}-related SHAP drivers"
        
        match = PlaybookMatch(
            playbook_id=playbook.get("playbook_id", ""),
            playbook_label=playbook.get("label", ""),
            category=playbook_category,
            confidence_tier=playbook.get("confidence_tier", "LOW"),
            source_project_count=playbook.get("source_project_count", 0),
            relevance_score=relevance,
            trigger_reason=trigger_reason,
        )
        
        matches.append(match)
    
    # Sort by relevance score
    matches.sort(key=lambda m: m.relevance_score, reverse=True)
    
    # Return top 1-3
    top_matches = matches[:3]
    
    logger.info(
        "Matched %d playbooks for project %s (risk: %s, shap categories: %s)",
        len(top_matches), project_id, risk_category, shap_categories
    )
    
    return top_matches


def generate_suggestions_for_projects(
    projects_data: list[dict],
    available_playbooks: list[dict],
) -> list[dict]:
    """Generate playbook suggestions for multiple projects.
    
    Args:
        projects_data: List of project dicts with:
            - project_id
            - composite_risk_score
            - risk_category
            - shap_drivers
            - reference_class_id
            - pbe_profile_similarity
        available_playbooks: List of available playbook dicts
    
    Returns:
        List of suggestion dicts for database storage
    """
    suggestions = []
    
    for project in projects_data:
        try:
            matches = match_playbooks_for_project(
                project_id=project.get("project_id", ""),
                composite_risk_score=project.get("composite_risk_score", 0),
                risk_category=project.get("risk_category", RiskCategory.LOW),
                shap_drivers=project.get("shap_drivers", []),
                reference_class_id=project.get("reference_class_id"),
                pbe_profile_similarity=project.get("pbe_profile_similarity", 0.5),
                available_playbooks=available_playbooks,
            )
            
            for match in matches:
                suggestion = {
                    "project_id": project.get("project_id"),
                    "playbook_id": match.playbook_id,
                    "triggered_by_risk_category": project.get("risk_category"),
                    "suggested_at": datetime.utcnow(),
                    "was_viewed": False,
                    "was_dismissed": False,
                    "relevance_score": match.relevance_score,
                    "trigger_reason": match.trigger_reason,
                }
                suggestions.append(suggestion)
                
        except Exception as exc:
            logger.error(
                "Failed to generate suggestions for project %s: %s",
                project.get("project_id"), exc
            )
    
    logger.info("Generated %d playbook suggestions for %d projects", len(suggestions), len(projects_data))
    return suggestions


class PlaybookMatcher:
    """Compatibility wrapper that exposes the expected playbook-matching API."""

    def __init__(self):
        self.risk_trigger_threshold = RISK_TRIGGER_THRESHOLD

    @staticmethod
    def _map_shap_feature_to_category(feature_name: str) -> str | None:
        return map_shap_to_category(feature_name)

    def match_playbooks(self, project: dict, playbooks: list[dict]) -> list[dict]:
        project_id = str(project.get("project_id", ""))
        risk_category = project.get("risk_category")
        if risk_category in {"LOW", RiskCategory.LOW.value, None}:
            return []

        shap_drivers = project.get("shap_drivers", []) or []
        shap_categories = []
        for driver in shap_drivers:
            feature = driver.get("feature") or driver.get("feature_name") or ""
            category = self._map_shap_feature_to_category(feature)
            if category:
                shap_categories.append(category)

        if not shap_categories:
            # fallback to any category available if risk-level triggers but SHAP mapping is absent
            shap_categories = [p.get("category") for p in playbooks if p.get("category")]

        scored = []
        for playbook in playbooks:
            category = playbook.get("category")
            if not category:
                continue

            if category not in shap_categories:
                continue

            reference_compat = playbook.get("reference_class_compatibility", []) or []
            project_sector = (project.get("pbe_profile") or {}).get("sector")
            project_size = (project.get("pbe_profile") or {}).get("size_band")
            reference_match = bool(
                reference_compat and (
                    project_sector in reference_compat or project_size in reference_compat
                )
            )

            source_count = int(playbook.get("source_project_count", 0))
            relevance_score = 0.6 if category in shap_categories else 0.3
            relevance_score += 0.2 if reference_match else 0.0
            relevance_score += min(source_count / 10.0, 0.2)
            relevance_score = round(min(relevance_score, 1.0), 4)

            suggestion = {
                "project_id": project_id,
                "playbook": {
                    "playbook_id": str(playbook.get("playbook_id", "")),
                    "category": category,
                    "label": playbook.get("label", ""),
                    "confidence_tier": playbook.get("confidence_tier", "LOW"),
                    "source_project_count": source_count,
                    "reference_class_compatibility": reference_compat,
                },
                "triggered_by_risk_category": risk_category,
                "trigger_reason": f"{category} risk driver is elevated",
                "relevance_score": relevance_score,
            }
            scored.append(suggestion)

        scored.sort(
            key=lambda s: (
                s["playbook"]["confidence_tier"] not in ["HIGH", "MEDIUM"],
                -int(s["playbook"].get("source_project_count", 0)),
                -float(s.get("relevance_score", 0.0)),
            )
        )
        return scored[:3]

    def get_all_playbooks(self, db):
        return []

    def get_suggestions(self, *args, **kwargs):
        return {"suggestions": [], "metadata": {}}
