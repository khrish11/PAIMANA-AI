"""SHAP explainability service for experimental PAIMANA models.

For every supported prediction, returns the top-5 drivers with:
- feature name, human label, value, contribution, direction, explanation.

Uses real shap.TreeExplainer for XGBoost and LightGBM where available.
Falls back to proportional decomposition for other cases.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, List
import numpy as np
import logging

logger = logging.getLogger(__name__)

# SHAP is optional - requires C++ build tools
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("SHAP not available (requires C++ build tools). Using fallback decomposition.")

from app.services.model_loader import get_model_loader


@dataclass(frozen=True)
class SHAPDriverResult:
    feature_name: str
    human_label: str
    feature_value: float | str
    contribution: float
    direction: str  # "increases_risk" or "decreases_risk"
    explanation: str


FEATURE_LABELS = {
    "original_cost_crore": "Original Cost (Crore)",
    "revised_cost_crore": "Revised Cost (Crore)",
    "cumulative_expenditure_crore": "Cumulative Expenditure (Crore)",
    "physical_progress_pct": "Physical Progress (%)",
    "cost_overrun_ratio": "Cost Overrun Ratio",
    "schedule_slip_months": "Schedule Slippage (months)",
    "expenditure_to_progress_gap": "Expenditure-Progress Gap",
    "progress_velocity_3m": "3-Month Progress Velocity",
    "cost_revision_count": "Number of Cost Revisions",
    "reporting_lag_days": "Reporting Lag (days)",
    "milestone_shift_count": "Milestone Shift Count",
    "governance_pending": "Pending Governance Review",
    "cost_risk": "Cost Risk Component",
    "schedule_risk": "Schedule Risk Component",
    "progress_anomaly_score": "Progress Anomaly Score",
    "governance_risk": "Governance Risk Component",
}


def _direction(contribution: float) -> str:
    return "increases_risk" if contribution > 0 else "decreases_risk"


def _explain_feature(name: str, value: float | str, contribution: float) -> str:
    label = FEATURE_LABELS.get(name, name.replace("_", " ").title())
    direction_text = "increasing" if contribution > 0 else "decreasing"

    explanations = {
        "original_cost_crore": f"Original cost of ₹{value} crore is {direction_text} the predicted risk.",
        "revised_cost_crore": f"Revised cost of ₹{value} crore is {direction_text} the predicted risk.",
        "cumulative_expenditure_crore": f"Cumulative expenditure of ₹{value} crore is {direction_text} the predicted risk.",
        "physical_progress_pct": f"Physical progress of {value}% is {direction_text} the predicted risk.",
        "cost_overrun_ratio": (
            f"Cost revision count is {value} and is {direction_text} predicted overrun risk."
            if name == "cost_revision_count"
            else f"Cost overrun ratio of {value} is {direction_text} the predicted risk."
        ),
        "schedule_slip_months": (
            f"Schedule has slipped by {value} months, {direction_text} schedule risk."
        ),
        "expenditure_to_progress_gap": (
            f"Gap of {value} between spending and physical progress is {direction_text} risk."
        ),
        "progress_velocity_3m": (
            f"3-month progress velocity of {value}% per month is {direction_text} risk."
        ),
        "cost_revision_count": (
            f"Cost has been revised {value} times, {direction_text} predicted overrun risk."
        ),
        "reporting_lag_days": (
            f"Reporting lag of {value} days is {direction_text} data confidence concerns."
        ),
        "cost_risk": (
            f"Cost risk score of {value} is {direction_text} the composite risk."
        ),
        "schedule_risk": (
            f"Schedule risk score of {value} is {direction_text} the composite risk."
        ),
        "progress_anomaly_score": (
            f"Progress anomaly score of {value} is {direction_text} the composite risk."
        ),
        "governance_risk": (
            f"Governance risk score of {value} is {direction_text} the composite risk."
        ),
    }
    return explanations.get(name, f"{label} value of {value} is {direction_text} the predicted risk.")


def explain_risk(
    *,
    cost_risk: float = 0.0,
    schedule_risk: float = 0.0,
    progress_anomaly_score: float = 0.0,
    governance_risk: float = 0.0,
    cost_overrun_ratio: float = 1.0,
    schedule_slip_months: float = 0.0,
    expenditure_to_progress_gap: float = 0.0,
    progress_velocity_3m: float = 0.0,
    cost_revision_count: int = 0,
    reporting_lag_days: int = 0,
    top_n: int = 5,
) -> list[SHAPDriverResult]:
    """Produce a deterministic feature-attribution explanation.

    This decomposes the composite risk into feature contributions
    proportional to how each input drives the overall score.
    """
    raw_features: list[tuple[str, float | str, float]] = [
        ("cost_risk", cost_risk, cost_risk * 0.30),
        ("schedule_risk", schedule_risk, schedule_risk * 0.25),
        ("progress_anomaly_score", progress_anomaly_score, progress_anomaly_score * 0.25),
        ("governance_risk", governance_risk, governance_risk * 0.20),
        ("cost_overrun_ratio", cost_overrun_ratio, max(0, (cost_overrun_ratio - 1.0)) * 50),
        ("schedule_slip_months", schedule_slip_months, min(30, schedule_slip_months * 2)),
        ("expenditure_to_progress_gap", round(expenditure_to_progress_gap, 3), expenditure_to_progress_gap * 40),
        ("cost_revision_count", cost_revision_count, min(15, cost_revision_count * 3)),
        ("reporting_lag_days", reporting_lag_days, min(10, max(0, reporting_lag_days - 15) * 0.2)),
        ("progress_velocity_3m", round(progress_velocity_3m, 2), max(0, -progress_velocity_3m) * 5),
    ]

    # Sort by absolute contribution, take top N
    sorted_features = sorted(raw_features, key=lambda x: abs(x[2]), reverse=True)[:top_n]

    drivers: list[SHAPDriverResult] = []
    for name, value, contribution in sorted_features:
        contribution = round(contribution, 2)
        if contribution == 0:
            continue
        drivers.append(
            SHAPDriverResult(
                feature_name=name,
                human_label=FEATURE_LABELS.get(name, name.replace("_", " ").title()),
                feature_value=value,
                contribution=contribution,
                direction=_direction(contribution),
                explanation=_explain_feature(name, value, contribution),
            )
        )

    return drivers


def explain_with_shap(
    model_type: str,
    project_data: Dict,
    top_n: int = 5
) -> Dict:
    """Generate SHAP explanations using real SHAP where available.
    
    Returns:
        Dict with status and either shap_drivers or error information
    """
    if not SHAP_AVAILABLE:
        return {
            'status': 'unavailable',
            'reason': 'SHAP not available (requires C++ build tools)',
            'shap_drivers': None
        }
    
    model_loader = get_model_loader()
    model_info = model_loader.get_model(model_type)
    
    if not model_info or not model_info.get('loaded'):
        return {
            'status': 'unavailable',
            'reason': f'Model {model_type} not loaded',
            'shap_drivers': None
        }
    
    try:
        model = model_info['model']
        
        # Extract features
        feature_names = [
            'original_cost_crore', 'revised_cost_crore',
            'cumulative_expenditure_crore', 'physical_progress_pct'
        ]
        
        features = []
        for fname in feature_names:
            val = project_data.get(fname)
            try:
                features.append(float(val) if val else 0.0)
            except (ValueError, TypeError):
                features.append(0.0)
        
        X = np.array([features])
        
        # Generate SHAP values
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        
        # Handle different SHAP output formats
        if isinstance(shap_values, list):
            shap_values = shap_values[0]  # Binary classification
        
        # Get top N features by absolute SHAP value
        abs_shap = np.abs(shap_values[0])
        top_indices = np.argsort(abs_shap)[-top_n:][::-1]
        
        shap_drivers = []
        for idx in top_indices:
            fname = feature_names[idx]
            fvalue = features[idx]
            shap_val = shap_values[0, idx]
            
            shap_drivers.append(SHAPDriverResult(
                feature_name=fname,
                human_label=FEATURE_LABELS.get(fname, fname.replace("_", " ").title()),
                feature_value=fvalue,
                contribution=float(shap_val),
                direction=_direction(shap_val),
                explanation=_explain_feature(fname, fvalue, shap_val)
            ))
        
        return {
            'status': 'success',
            'shap_drivers': shap_drivers
        }
        
    except Exception as e:
        logger.error(f"SHAP generation failed for {model_type}: {e}")
        return {
            'status': 'error',
            'reason': str(e),
            'shap_drivers': None
        }
