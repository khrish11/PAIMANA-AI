"""Model registry / admin API route (SRS Section 6.5)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import csv
import json

from fastapi import APIRouter, Depends

from app.core.security import Role, require_role
from app.schemas.schemas import ModelPerformanceEntry, ModelPerformanceResponse

router = APIRouter(prefix="/admin", tags=["admin"])


def load_experimental_model_metrics(data_dir: Path) -> dict:
    """Load experimental model metrics from data files."""
    # Load model comparison CSV
    comparison_path = data_dir / 'results' / 'model_comparison.csv'
    comparison_data = {}
    
    if comparison_path.exists():
        with open(comparison_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                comparison_data[row['model']] = row
    
    # Load detailed metrics JSON
    metrics_path = data_dir / 'results' / 'experimental_model_metrics.json'
    detailed_metrics = {}
    
    if metrics_path.exists():
        with open(metrics_path, 'r', encoding='utf-8') as f:
            detailed_metrics = json.load(f)
    
    return comparison_data, detailed_metrics


@router.get("/models", response_model=ModelPerformanceResponse)
def list_models(
    user: Any = Depends(require_role(Role.ANALYST)),
):
    """List all registered models with performance metrics.
    
    Returns actual experimental model metrics from PAIMANA real data.
    Includes model availability status from model loader.
    """
    from app.core.config import settings
    from app.services.model_loader import get_model_loader
    data_dir = Path(settings.data_dir)
    
    comparison_data, detailed_metrics = load_experimental_model_metrics(data_dir)
    
    # Get model availability from model loader
    model_loader = get_model_loader()
    
    models = []
    
    # Add experimental models
    for model_type in ['random_forest', 'xgboost', 'lightgbm']:
        if model_type in detailed_metrics:
            metrics = detailed_metrics[model_type]
            comparison = comparison_data.get(model_type, {})
            
            # Get model availability
            model_info = model_loader.get_model(model_type)
            available = model_info.get('loaded', False) if model_info else False
            availability_reason = model_info.get('error') if model_info and not available else None
            
            models.append(ModelPerformanceEntry(
                model_type=model_type,
                version=f"{model_type}-exp-v1",
                precision=metrics.get('precision', comparison.get('precision')),
                recall=metrics.get('recall', comparison.get('recall')),
                f1=metrics.get('f1', comparison.get('f1')),
                roc_auc=metrics.get('roc_auc', comparison.get('roc_auc')),
                pr_auc=metrics.get('pr_auc', comparison.get('pr_auc')),
                brier_score=metrics.get('brier', comparison.get('brier')),
                balanced_accuracy=metrics.get('balanced_accuracy'),
                mcc=metrics.get('mcc'),
                trained_date="2026-08-28",
                is_active=False,  # All experimental models are inactive
                sector_performance={},
                available=available,
                availability_reason=availability_reason,
                target="delay_gt_6_months",
                status="EXPERIMENTAL",
                holdout_size=5,
                training_period="2024-01 to 2026-06",
                validation_period="2026-07",
                notes="EXPERIMENTAL - Limited completed outcomes (160 projects). Not production validated.",
            ))
    
    # Add baseline models for comparison
    for model_type in ['majority_class', 'logistic_regression']:
        if model_type in comparison_data:
            comp = comparison_data[model_type]
            
            models.append(ModelPerformanceEntry(
                model_type=model_type,
                version=f"{model_type}-baseline-v1",
                precision=float(comp.get('precision', 0)),
                recall=float(comp.get('recall', 0)),
                f1=float(comp.get('f1', 0)),
                roc_auc=float(comp.get('roc_auc', 0)),
                pr_auc=float(comp.get('pr_auc', 0)),
                brier_score=float(comp.get('brier', 0)),
                trained_date="2026-08-28",
                is_active=False,
                sector_performance={},
                notes="Baseline model for comparison.",
            ))
    
    active = None  # No active models (all experimental)
    
    return ModelPerformanceResponse(
        models=models,
        active_model=active,
        data_source="real_paimana_experimental",
        holdout_size=5,
        holdout_warning="July 2026 holdout contains only 5 labelled projects; metrics are indicative only.",
    )
