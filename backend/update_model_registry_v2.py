"""Update model registry with v2 model artifacts."""

import json
from pathlib import Path
from datetime import datetime


def update_model_registry():
    """Update model registry with v2 models."""
    print("=" * 80)
    print("MODEL REGISTRY UPDATE V2")
    print("=" * 80)
    
    # 1. Load existing registry
    print("\n1. LOADING EXISTING REGISTRY")
    print("-" * 80)
    
    registry_path = Path('../data/artifacts/model_registry.json')
    if not registry_path.exists():
        registry_path = Path('data/artifacts/model_registry.json')
    
    if registry_path.exists():
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        print(f"Loaded existing registry with {len(registry.get('models', []))} models")
    else:
        registry = {
            'version': '1.0',
            'last_updated': None,
            'models': []
        }
        print("No existing registry found, creating new")
    
    # 2. Define v2 models
    print("\n2. DEFINING V2 MODELS")
    print("-" * 80)
    
    v2_models = [
        {
            'id': 'random_forest_cost_v2',
            'name': 'Random Forest Cost Overrun v2',
            'version': '2.0',
            'type': 'cost_overrun',
            'algorithm': 'random_forest',
            'target': 'cost_overrun_10pct',
            'status': 'EXPERIMENTAL',
            'artifact_path': 'data/artifacts/experimental/v2/random_forest_cost_v2.pkl',
            'feature_path': 'data/artifacts/experimental/v2/cost_feature_names_v2.json',
            'training_date': '2026-08-31',
            'training_samples': 274,
            'validation_samples': 90,
            'test_samples': 90,
            'target_prevalence': 0.504,
            'metrics': {
                'train_f1': 0.855,
                'val_f1': 0.818,
                'test_f1': 0.785,
                'val_roc_auc': 0.740,
                'test_roc_auc': 0.796,
                'val_pr_auc': 0.655,
                'test_pr_auc': 0.708,
                'val_brier': 0.170,
                'test_brier': 0.167,
                'val_mcc': 0.603,
                'test_mcc': 0.561
            },
            'calibration': 'uncalibrated',
            'shap': 'partial (compatibility issue)',
            'notes': 'Trained on 454 completed projects (2.8x increase from v1)'
        },
        {
            'id': 'xgboost_cost_v2',
            'name': 'XGBoost Cost Overrun v2',
            'version': '2.0',
            'type': 'cost_overrun',
            'algorithm': 'xgboost',
            'target': 'cost_overrun_10pct',
            'status': 'EXPERIMENTAL_SELECTED',
            'artifact_path': 'data/artifacts/experimental/v2/xgboost_cost_v2.pkl',
            'feature_path': 'data/artifacts/experimental/v2/cost_feature_names_v2.json',
            'training_date': '2026-08-31',
            'training_samples': 274,
            'validation_samples': 90,
            'test_samples': 90,
            'target_prevalence': 0.504,
            'metrics': {
                'train_f1': 0.937,
                'val_f1': 0.645,
                'test_f1': 0.723,
                'val_roc_auc': 0.728,
                'test_roc_auc': 0.809,
                'val_pr_auc': 0.650,
                'test_pr_auc': 0.747,
                'val_brier': 0.228,
                'test_brier': 0.187,
                'val_mcc': 0.266,
                'test_mcc': 0.487
            },
            'calibration': 'uncalibrated',
            'shap': 'working',
            'notes': 'Best cost model (Test ROC-AUC: 0.809)'
        },
        {
            'id': 'lightgbm_cost_v2',
            'name': 'LightGBM Cost Overrun v2',
            'version': '2.0',
            'type': 'cost_overrun',
            'algorithm': 'lightgbm',
            'target': 'cost_overrun_10pct',
            'status': 'EXPERIMENTAL',
            'artifact_path': 'data/artifacts/experimental/v2/lightgbm_cost_v2.pkl',
            'feature_path': 'data/artifacts/experimental/v2/cost_feature_names_v2.json',
            'training_date': '2026-08-31',
            'training_samples': 274,
            'validation_samples': 90,
            'test_samples': 90,
            'target_prevalence': 0.504,
            'metrics': {
                'train_f1': 0.903,
                'val_f1': 0.681,
                'test_f1': 0.769,
                'val_roc_auc': 0.715,
                'test_roc_auc': 0.778,
                'val_pr_auc': 0.627,
                'test_pr_auc': 0.676,
                'val_brier': 0.211,
                'test_brier': 0.180,
                'val_mcc': 0.333,
                'test_mcc': 0.538
            },
            'calibration': 'uncalibrated',
            'shap': 'working',
            'notes': 'LightGBM libgomp.so.1 issue resolved on Windows (v4.3.0)'
        },
        {
            'id': 'random_forest_schedule_v2',
            'name': 'Random Forest Schedule Delay v2',
            'version': '2.0',
            'type': 'schedule_delay',
            'algorithm': 'random_forest',
            'target': 'delay_gt_6_months',
            'status': 'EXPERIMENTAL',
            'artifact_path': 'data/artifacts/experimental/v2/random_forest_schedule_v2.pkl',
            'feature_path': 'data/artifacts/experimental/v2/schedule_feature_names_v2.json',
            'training_date': '2026-08-31',
            'training_samples': 252,
            'validation_samples': 85,
            'test_samples': 85,
            'target_prevalence': 0.710,
            'metrics': {
                'train_f1': 0.825,
                'val_f1': 0.800,
                'test_f1': 0.780,
                'val_roc_auc': 0.653,
                'test_roc_auc': 0.741,
                'val_pr_auc': 0.800,
                'test_pr_auc': 0.865,
                'val_brier': 0.206,
                'test_brier': 0.205,
                'val_mcc': 0.247,
                'test_mcc': 0.281
            },
            'calibration': 'uncalibrated',
            'shap': 'partial (compatibility issue)',
            'notes': 'Trained with stratified split to fix temporal label shift'
        },
        {
            'id': 'xgboost_schedule_v2',
            'name': 'XGBoost Schedule Delay v2',
            'version': '2.0',
            'type': 'schedule_delay',
            'algorithm': 'xgboost',
            'target': 'delay_gt_6_months',
            'status': 'EXPERIMENTAL',
            'artifact_path': 'data/artifacts/experimental/v2/xgboost_schedule_v2.pkl',
            'feature_path': 'data/artifacts/experimental/v2/schedule_feature_names_v2.json',
            'training_date': '2026-08-31',
            'training_samples': 252,
            'validation_samples': 85,
            'test_samples': 85,
            'target_prevalence': 0.710,
            'metrics': {
                'train_f1': 0.776,
                'val_f1': 0.759,
                'test_f1': 0.750,
                'val_roc_auc': 0.694,
                'test_roc_auc': 0.718,
                'val_pr_auc': 0.814,
                'test_pr_auc': 0.826,
                'val_brier': 0.203,
                'test_brier': 0.207,
                'val_mcc': 0.248,
                'test_mcc': 0.280
            },
            'calibration': 'uncalibrated',
            'shap': 'working',
            'notes': 'Trained with stratified split to fix temporal label shift'
        },
        {
            'id': 'lightgbm_schedule_v2',
            'name': 'LightGBM Schedule Delay v2',
            'version': '2.0',
            'type': 'schedule_delay',
            'algorithm': 'lightgbm',
            'target': 'delay_gt_6_months',
            'status': 'EXPERIMENTAL_SELECTED',
            'artifact_path': 'data/artifacts/experimental/v2/lightgbm_schedule_v2.pkl',
            'feature_path': 'data/artifacts/experimental/v2/schedule_feature_names_v2.json',
            'training_date': '2026-08-31',
            'training_samples': 252,
            'validation_samples': 85,
            'test_samples': 85,
            'target_prevalence': 0.710,
            'metrics': {
                'train_f1': 0.811,
                'val_f1': 0.806,
                'test_f1': 0.857,
                'val_roc_auc': 0.695,
                'test_roc_auc': 0.757,
                'val_pr_auc': 0.830,
                'test_pr_auc': 0.854,
                'val_brier': 0.224,
                'test_brier': 0.208,
                'val_mcc': 0.121,
                'test_mcc': 0.406
            },
            'calibration': 'uncalibrated',
            'shap': 'working',
            'notes': 'Best schedule model (Test ROC-AUC: 0.757), trained with stratified split'
        }
    ]
    
    print(f"Defined {len(v2_models)} v2 models")
    
    # 3. Add v2 models to registry
    print("\n3. ADDING V2 MODELS TO REGISTRY")
    print("-" * 80)
    
    # Mark existing models as deprecated
    for model in registry.get('models', []):
        if model.get('version') == '1.0':
            model['status'] = 'DEPRECATED'
            model['deprecated_date'] = '2026-08-31'
            model['deprecation_reason'] = 'Replaced by v2 models trained on 454 completed projects'
    
    # Add v2 models
    registry['models'].extend(v2_models)
    
    print(f"Total models in registry: {len(registry['models'])}")
    
    # 4. Update registry metadata
    print("\n4. UPDATING REGISTRY METADATA")
    print("-" * 80)
    
    registry['version'] = '2.0'
    registry['last_updated'] = datetime.now().isoformat()
    registry['dataset_version'] = 'v2'
    registry['dataset_size'] = 454
    registry['notes'] = 'v2 models trained on 454 completed projects with comprehensive diagnostics'
    
    # 5. Save registry
    print("\n5. SAVING REGISTRY")
    print("-" * 80)
    
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"Saved registry to {registry_path}")
    
    # 6. Summary
    print("\n6. SUMMARY")
    print("-" * 80)
    
    print(f"Registry version: {registry['version']}")
    print(f"Last updated: {registry['last_updated']}")
    print(f"Dataset version: {registry['dataset_version']}")
    print(f"Dataset size: {registry['dataset_size']}")
    
    print("\nModel status:")
    for model in registry['models']:
        model_id = model.get('id', model.get('name', 'unknown'))
        model_status = model.get('status', 'unknown')
        print(f"  {model_id}: {model_status}")
    
    return registry


if __name__ == "__main__":
    result = update_model_registry()
