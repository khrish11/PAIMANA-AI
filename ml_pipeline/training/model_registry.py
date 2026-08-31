"""Model registry for experimental PAIMANA models.

Registers models with EXPERIMENTAL status.
"""

import csv
import json
import joblib
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class ModelRegistry:
    """Registry for experimental models."""
    
    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self.registry = self.load_registry()
    
    def load_registry(self) -> Dict:
        """Load existing registry or create new."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {'models': [], 'version': '1.0'}
    
    def save_registry(self):
        """Save registry to disk."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_model(self, model_info: Dict):
        """Register a model in the registry."""
        model_info['registered_at'] = datetime.now().isoformat()
        self.registry['models'].append(model_info)
        self.save_registry()
    
    def get_active_model(self, model_type: str) -> Dict:
        """Get active model of given type."""
        for model in self.registry['models']:
            if model.get('model_type') == model_type and model.get('active'):
                return model
        return None


def register_experimental_models(data_dir: Path, metrics: Dict):
    """Register experimental models in registry."""
    registry_path = data_dir / 'artifacts' / 'model_registry.json'
    registry = ModelRegistry(registry_path)
    
    # Register Random Forest
    rf_info = {
        'model_type': 'random_forest',
        'version': 'rf-exp-v1',
        'status': 'experimental',
        'active': False,  # Not active for production
        'target': 'delay_gt_6_months',
        'training_period': '2025-07 to 2026-06',
        'validation_period': '2026-07',
        'holdout_period': '2026-07',
        'feature_version': 'v1',
        'metrics': metrics['random_forest'],
        'artifact_path': str(data_dir / 'artifacts' / 'experimental' / 'random_forest_experimental.pkl'),
        'calibration_status': 'not_calibrated',
        'limitations': [
            'Small sample size (160 labeled projects)',
            'Class imbalance (60% positive)',
            'Short temporal window (13 months)',
            'Not production-validated'
        ]
    }
    registry.register_model(rf_info)
    
    # Register XGBoost
    xgb_info = {
        'model_type': 'xgboost',
        'version': 'xgb-exp-v1',
        'status': 'experimental',
        'active': False,
        'target': 'delay_gt_6_months',
        'training_period': '2025-07 to 2026-06',
        'validation_period': '2026-07',
        'holdout_period': '2026-07',
        'feature_version': 'v1',
        'metrics': metrics['xgboost'],
        'artifact_path': str(data_dir / 'artifacts' / 'experimental' / 'xgboost_experimental.pkl'),
        'calibration_status': 'not_calibrated',
        'limitations': [
            'Small sample size (160 labeled projects)',
            'Class imbalance (60% positive)',
            'Short temporal window (13 months)',
            'Not production-validated'
        ]
    }
    registry.register_model(xgb_info)
    
    # Register LightGBM
    lgb_info = {
        'model_type': 'lightgbm',
        'version': 'lgb-exp-v1',
        'status': 'experimental',
        'active': False,
        'target': 'delay_gt_6_months',
        'training_period': '2025-07 to 2026-06',
        'validation_period': '2026-07',
        'holdout_period': '2026-07',
        'feature_version': 'v1',
        'metrics': metrics['lightgbm'],
        'artifact_path': str(data_dir / 'artifacts' / 'experimental' / 'lightgbm_experimental.pkl'),
        'calibration_status': 'not_calibrated',
        'limitations': [
            'Small sample size (160 labeled projects)',
            'Class imbalance (60% positive)',
            'Short temporal window (13 months)',
            'Not production-validated'
        ]
    }
    registry.register_model(lgb_info)
    
    print(f"Model registry updated: {registry_path}")
    print(f"Registered models: {len(registry.registry['models'])}")
    
    return registry.registry


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    
    # Load metrics from experimental training
    with open(data_dir / 'results' / 'experimental_model_metrics.json', 'r') as f:
        metrics = json.load(f)
    
    registry = register_experimental_models(data_dir, metrics)
    
    print("\nRegistered Models:")
    for model in registry['models']:
        print(f"  {model['model_type']} - {model['version']} - {model['status']}")
