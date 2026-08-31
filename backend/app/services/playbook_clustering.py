"""Playbook Clustering service.

Clusters extracted actions from positive deviants into evidence-backed playbooks.
Uses sentence-transformers for embeddings with fallback to deterministic text similarity.

Hard guardrail: A playbook MUST contain actions from >= 3 DIFFERENT PROJECTS.

Confidence tiers:
- 3 projects = LOW
- 4-6 projects = MEDIUM
- 7+ projects = HIGH
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from typing import Literal

import numpy as np

logger = logging.getLogger(__name__)

# Minimum independent projects required for a playbook
MIN_INDEPENDENT_PROJECTS = 3

# Confidence tier thresholds
LOW_THRESHOLD = 3
MEDIUM_THRESHOLD = 4
HIGH_THRESHOLD = 7

# Clustering parameters
SIMILARITY_THRESHOLD = 0.7  # For deterministic fallback
EMBEDDING_THRESHOLD = 0.75  # For embedding-based clustering


@dataclass(frozen=True)
class PlaybookCluster:
    """A cluster of similar actions forming a playbook."""
    category: str
    label: str
    action_ids: list[str]
    project_ids: set[str]
    source_project_count: int
    confidence_tier: Literal["LOW", "MEDIUM", "HIGH"]
    is_fallback: bool


def _calculate_confidence_tier(project_count: int) -> Literal["LOW", "MEDIUM", "HIGH"]:
    """Calculate confidence tier based on source project count.
    
    Args:
        project_count: Number of independent source projects
    
    Returns:
        Confidence tier
    """
    if project_count >= HIGH_THRESHOLD:
        return "HIGH"
    if project_count >= MEDIUM_THRESHOLD:
        return "MEDIUM"
    return "LOW"


def _text_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity using SequenceMatcher (deterministic fallback).
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score between 0 and 1
    """
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def _get_embedding(text: str, model=None) -> np.ndarray | None:
    """Get embedding for text using sentence-transformers.
    
    Args:
        text: Text to embed
        model: SentenceTransformer model (optional, for caching)
    
    Returns:
        Embedding vector or None if unavailable
    """
    try:
        from sentence_transformers import SentenceTransformer
        
        if model is None:
            model = SentenceTransformer('all-MiniLM-L6-v2')
        
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding
    except ImportError:
        logger.warning("sentence-transformers not available, using fallback similarity")
        return None
    except Exception as exc:
        logger.error("Failed to generate embedding: %s", exc)
        return None


def _cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """Calculate cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
    
    Returns:
        Cosine similarity score
    """
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def cluster_actions_by_category(
    actions: list[dict],
    use_embeddings: bool = True,
) -> list[PlaybookCluster]:
    """Cluster actions into playbooks by category.
    
    Args:
        actions: List of extracted action dictionaries with:
            - action_id
            - project_id
            - action_text
            - category
        use_embeddings: Whether to use sentence-transformers (True) or fallback (False)
    
    Returns:
        List of PlaybookCluster objects
    """
    # Group actions by category
    by_category = defaultdict(list)
    for action in actions:
        category = action.get("category", "other")
        by_category[category].append(action)
    
    clusters = []
    embedding_model = None
    
    if use_embeddings:
        # Try to load embedding model once
        try:
            from sentence_transformers import SentenceTransformer
            embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Using sentence-transformers for clustering")
        except ImportError:
            logger.warning("sentence-transformers not available, using fallback")
            use_embeddings = False
    
    # Cluster within each category
    for category, category_actions in by_category.items():
        if len(category_actions) < MIN_INDEPENDENT_PROJECTS:
            logger.debug(
                "Skipping category %s: insufficient unique projects (%d < %d)",
                category, len(set(a.get("project_id") for a in category_actions)), MIN_INDEPENDENT_PROJECTS
            )
            continue
        
        if use_embeddings and embedding_model is not None:
            category_clusters = _cluster_with_embeddings(category_actions, category, embedding_model)
        else:
            category_clusters = _cluster_with_similarity(category_actions, category)
        
        clusters.extend(category_clusters)
    
    logger.info("Generated %d playbook clusters from %d actions", len(clusters), len(actions))
    return clusters


def _cluster_with_embeddings(
    actions: list[dict],
    category: str,
    model,
) -> list[PlaybookCluster]:
    """Cluster actions using sentence-transformer embeddings.
    
    Args:
        actions: List of actions in this category
        category: The category name
        model: SentenceTransformer model
    
    Returns:
        List of PlaybookCluster objects
    """
    # Generate embeddings
    embeddings = []
    for action in actions:
        embedding = _get_embedding(action.get("action_text", ""), model)
        if embedding is not None:
            embeddings.append(embedding)
        else:
            # Fallback to zero vector if embedding fails
            embeddings.append(np.zeros(384))  # all-MiniLM-L6-v2 dimension
    
    embeddings = np.array(embeddings)
    
    # Simple clustering: group by similarity threshold
    # In production, would use DBSCAN or agglomerative clustering
    clusters = []
    assigned = set()
    
    for i, action in enumerate(actions):
        if i in assigned:
            continue
        
        # Find similar actions
        similar_indices = [i]
        for j in range(len(actions)):
            if j != i and j not in assigned:
                similarity = _cosine_similarity(embeddings[i], embeddings[j])
                if similarity >= EMBEDDING_THRESHOLD:
                    similar_indices.append(j)
        
        # Check if we have enough independent projects
        similar_actions = [actions[idx] for idx in similar_indices]
        unique_projects = set(a.get("project_id") for a in similar_actions)
        
        if len(unique_projects) >= MIN_INDEPENDENT_PROJECTS:
            # Create a cluster
            cluster = PlaybookCluster(
                category=category,
                label=_generate_cluster_label(similar_actions, category),
                action_ids=[a.get("action_id") for a in similar_actions],
                project_ids=unique_projects,
                source_project_count=len(unique_projects),
                confidence_tier=_calculate_confidence_tier(len(unique_projects)),
                is_fallback=False,
            )
            clusters.append(cluster)
            
            # Mark as assigned
            for idx in similar_indices:
                assigned.add(idx)
    
    return clusters


def _cluster_with_similarity(
    actions: list[dict],
    category: str,
) -> list[PlaybookCluster]:
    """Cluster actions using deterministic text similarity (fallback).
    
    Args:
        actions: List of actions in this category
        category: The category name
    
    Returns:
        List of PlaybookCluster objects
    """
    clusters = []
    assigned = set()
    
    for i, action in enumerate(actions):
        if i in assigned:
            continue
        
        # Find similar actions
        similar_indices = [i]
        for j in range(len(actions)):
            if j != i and j not in assigned:
                similarity = _text_similarity(
                    action.get("action_text", ""),
                    actions[j].get("action_text", "")
                )
                if similarity >= SIMILARITY_THRESHOLD:
                    similar_indices.append(j)
        
        # Check if we have enough independent projects
        similar_actions = [actions[idx] for idx in similar_indices]
        unique_projects = set(a.get("project_id") for a in similar_actions)
        
        if len(unique_projects) >= MIN_INDEPENDENT_PROJECTS:
            # Create a cluster
            cluster = PlaybookCluster(
                category=category,
                label=_generate_cluster_label(similar_actions, category),
                action_ids=[a.get("action_id") for a in similar_actions],
                project_ids=unique_projects,
                source_project_count=len(unique_projects),
                confidence_tier=_calculate_confidence_tier(len(unique_projects)),
                is_fallback=True,  # Mark as fallback method
            )
            clusters.append(cluster)
            
            # Mark as assigned
            for idx in similar_indices:
                assigned.add(idx)
    
    return clusters


def _generate_cluster_label(actions: list[dict], category: str) -> str:
    """Generate a descriptive label for a cluster.
    
    Args:
        actions: Actions in the cluster
        category: The category name
    
    Returns:
        Descriptive label
    """
    if not actions:
        return f"{category} Practice"
    
    # Extract common words/phrases from action texts
    action_texts = [a.get("action_text", "") for a in actions]
    
    # Simple approach: take the first action's text and truncate
    first_action = action_texts[0]
    if len(first_action) > 100:
        label = first_action[:97] + "..."
    else:
        label = first_action
    
    return label


def generate_playbooks_from_clusters(
    clusters: list[PlaybookCluster],
) -> list[dict]:
    """Convert clusters to playbook format for database storage.
    
    Args:
        clusters: List of PlaybookCluster objects
    
    Returns:
        List of playbook dictionaries
    """
    playbooks = []
    
    for cluster in clusters:
        playbook = {
            "category": cluster.category,
            "label": cluster.label,
            "confidence_tier": cluster.confidence_tier,
            "source_action_ids": cluster.action_ids,
            "source_project_count": cluster.source_project_count,
            "created_at": datetime.utcnow(),
            "last_updated_at": datetime.utcnow(),
            "is_fallback": cluster.is_fallback,
        }
        playbooks.append(playbook)
    
    logger.info("Generated %d playbooks from %d clusters", len(playbooks), len(clusters))
    return playbooks


class PlaybookClusterer:
    """Compatibility wrapper for clustering extracted actions into playbooks."""

    def cluster_actions(self, actions: list[dict], category: str | None = None) -> list[dict]:
        if not actions:
            return []

        if category is None:
            category = actions[0].get("category", "other")

        grouped = [action for action in actions if not category or action.get("category") == category]
        if not grouped:
            return []

        by_project = defaultdict(set)
        for action in grouped:
            by_project[action.get("project_id")].add(action.get("action_id"))

        # Guardrail: require at least 3 independent projects.
        project_ids = sorted(by_project)
        if len(project_ids) < MIN_INDEPENDENT_PROJECTS:
            return []

        cluster = {
            "category": category,
            "label": _generate_cluster_label(grouped, category),
            "source_action_ids": [a.get("action_id") for a in grouped],
            "source_project_count": len(project_ids),
            "confidence_tier": _calculate_confidence_tier(len(project_ids)),
        }
        return [cluster]

    def get_all_playbooks(self, db):
        return []

    def get_playbook_detail(self, playbook_id):
        return {"playbook_id": playbook_id, "evidence_actions": []}
