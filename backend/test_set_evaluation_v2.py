"""One-time final evaluation on test set."""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
from sklearn.metrics import (
    precision_score, recall_score, f1_score, 
    roc_auc_score, average_precision_score, brier_score_loss,
    matthews_corrcoef, balanced_accuracy_score, confusion_matrix
)


def evaluate_on_test_set(model, X_test, y_test, model_name):
    """Evaluate model on test set."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    metrics = {
        'model': model_name,
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_proba) if len(np.unique(y_test)) > 1 else 0,
        'pr_auc': average_precision_score(y_test, y_proba) if len(np.unique(y_test)) > 1 else 0,
        'brier': brier_score_loss(y_test, y_proba),
        'mcc': matthews_corrcoef(y_test, y_pred),
        'balanced_accuracy': balanced_accuracy_score(y_test, y_pred),
        'tn': tn,
        'fp': fp,
        'fn': fn,
        'tp': tp
    }
    return metrics


def test_set_evaluation():
    """One-time final evaluation on test set."""
    print("=" * 80)
    print("TEST SET EVALUATION V2")
    print("=" * 80)
    
    # 1. Load data and models
    print("\n1. LOADING DATA AND MODELS")
    print("-" * 80)
    
    data_dir = Path('../data/training/v2')
    if not data_dir.exists():
        data_dir = Path('data/training/v2')
    
    artifacts_dir = Path('../data/artifacts/experimental/v2')
    if not artifacts_dir.exists():
        artifacts_dir = Path('data/artifacts/experimental/v2')
    
    # Load cost data
    X_cost_test = pd.read_csv(data_dir / 'cost_overrun_test_features.csv')
    y_cost_test = X_cost_test['cost_overrun_10pct']
    
    with open(data_dir / 'cost_feature_names.json', 'r') as f:
        cost_feature_names = json.load(f)
    
    X_cost_test = X_cost_test[cost_feature_names].fillna(0)
    
    # Load schedule data
    X_schedule_test = pd.read_csv(data_dir / 'schedule_delay_test_features.csv')
    y_schedule_test = X_schedule_test['delay_gt_6_months']
    
    with open(data_dir / 'schedule_feature_names.json', 'r') as f:
        schedule_feature_names = json.load(f)
    
    X_schedule_test = X_schedule_test[schedule_feature_names].fillna(0)
    
    # Load models
    with open(artifacts_dir / 'random_forest_cost_v2.pkl', 'rb') as f:
        rf_cost = pickle.load(f)
    with open(artifacts_dir / 'xgboost_cost_v2.pkl', 'rb') as f:
        xgb_cost = pickle.load(f)
    with open(artifacts_dir / 'lightgbm_cost_v2.pkl', 'rb') as f:
        lgb_cost = pickle.load(f)
    
    with open(artifacts_dir / 'random_forest_schedule_v2.pkl', 'rb') as f:
        rf_schedule = pickle.load(f)
    with open(artifacts_dir / 'xgboost_schedule_v2.pkl', 'rb') as f:
        xgb_schedule = pickle.load(f)
    with open(artifacts_dir / 'lightgbm_schedule_v2.pkl', 'rb') as f:
        lgb_schedule = pickle.load(f)
    
    print(f"Cost test samples: {len(X_cost_test)}, Positive rate: {y_cost_test.mean():.3f}")
    print(f"Schedule test samples: {len(X_schedule_test)}, Positive rate: {y_schedule_test.mean():.3f}")
    
    # 2. Cost test evaluation
    print("\n2. COST TEST EVALUATION")
    print("-" * 80)
    
    cost_test_results = []
    for model, name in [(rf_cost, "Random Forest"), (xgb_cost, "XGBoost"), (lgb_cost, "LightGBM")]:
        metrics = evaluate_on_test_set(model, X_cost_test, y_cost_test, name)
        cost_test_results.append(metrics)
        print(f"{name}:")
        print(f"  F1: {metrics['f1']:.3f}, ROC-AUC: {metrics['roc_auc']:.3f}, PR-AUC: {metrics['pr_auc']:.3f}")
        print(f"  Precision: {metrics['precision']:.3f}, Recall: {metrics['recall']:.3f}")
        print(f"  Brier: {metrics['brier']:.3f}, MCC: {metrics['mcc']:.3f}")
    
    # 3. Schedule test evaluation
    print("\n3. SCHEDULE TEST EVALUATION")
    print("-" * 80)
    
    schedule_test_results = []
    for model, name in [(rf_schedule, "Random Forest"), (xgb_schedule, "XGBoost"), (lgb_schedule, "LightGBM")]:
        metrics = evaluate_on_test_set(model, X_schedule_test, y_schedule_test, name)
        schedule_test_results.append(metrics)
        print(f"{name}:")
        print(f"  F1: {metrics['f1']:.3f}, ROC-AUC: {metrics['roc_auc']:.3f}, PR-AUC: {metrics['pr_auc']:.3f}")
        print(f"  Precision: {metrics['precision']:.3f}, Recall: {metrics['recall']:.3f}")
        print(f"  Brier: {metrics['brier']:.3f}, MCC: {metrics['mcc']:.3f}")
    
    # 4. Summary
    print("\n4. SUMMARY")
    print("-" * 80)
    
    print("Cost Overrun - Test Set:")
    best_cost = max(cost_test_results, key=lambda x: x['roc_auc'])
    print(f"  Best: {best_cost['model']} with ROC-AUC = {best_cost['roc_auc']:.3f}")
    
    print("\nSchedule Delay - Test Set:")
    best_schedule = max(schedule_test_results, key=lambda x: x['roc_auc'])
    print(f"  Best: {best_schedule['model']} with ROC-AUC = {best_schedule['roc_auc']:.3f}")
    
    return {
        'cost_test_results': cost_test_results,
        'schedule_test_results': schedule_test_results
    }


if __name__ == "__main__":
    result = test_set_evaluation()
