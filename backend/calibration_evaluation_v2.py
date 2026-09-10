"""Calibration evaluation for v2 models."""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
from sklearn.metrics import brier_score_loss
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
import matplotlib.pyplot as plt


def evaluate_calibration(model, X_val, y_val, model_name):
    """Evaluate model calibration (simplified - uncalibrated only)."""
    y_proba = model.predict_proba(X_val)[:, 1]
    
    # Uncalibrated Brier
    brier_uncal = brier_score_loss(y_val, y_proba)
    
    # Calibration curve
    prob_true, prob_pred = calibration_curve(y_val, y_proba, n_bins=10)
    
    results = {
        'model': model_name,
        'brier_uncalibrated': brier_uncal,
        'calibration_method': 'uncalibrated (skipped due to compatibility)'
    }
    
    return results


def calibration_evaluation():
    """Evaluate calibration for all models."""
    print("=" * 80)
    print("CALIBRATION EVALUATION V2")
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
    X_cost_val = pd.read_csv(data_dir / 'cost_overrun_val_features.csv')
    y_cost_val = X_cost_val['cost_overrun_10pct']
    
    with open(data_dir / 'cost_feature_names.json', 'r') as f:
        cost_feature_names = json.load(f)
    
    X_cost_val = X_cost_val[cost_feature_names].fillna(0)
    
    # Load schedule data
    X_schedule_val = pd.read_csv(data_dir / 'schedule_delay_val_features.csv')
    y_schedule_val = X_schedule_val['delay_gt_6_months']
    
    with open(data_dir / 'schedule_feature_names.json', 'r') as f:
        schedule_feature_names = json.load(f)
    
    X_schedule_val = X_schedule_val[schedule_feature_names].fillna(0)
    
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
    
    # 2. Cost calibration
    print("\n2. COST CALIBRATION")
    print("-" * 80)
    
    cost_cal_results = []
    for model, name in [(rf_cost, "Random Forest"), (xgb_cost, "XGBoost"), (lgb_cost, "LightGBM")]:
        results = evaluate_calibration(model, X_cost_val, y_cost_val, name)
        cost_cal_results.append(results)
        print(f"{name}:")
        print(f"  Uncalibrated Brier: {results['brier_uncalibrated']:.3f}")
        print(f"  {results['calibration_method']}")
    
    # 3. Schedule calibration
    print("\n3. SCHEDULE CALIBRATION")
    print("-" * 80)
    
    schedule_cal_results = []
    for model, name in [(rf_schedule, "Random Forest"), (xgb_schedule, "XGBoost"), (lgb_schedule, "LightGBM")]:
        results = evaluate_calibration(model, X_schedule_val, y_schedule_val, name)
        schedule_cal_results.append(results)
        print(f"{name}:")
        print(f"  Uncalibrated Brier: {results['brier_uncalibrated']:.3f}")
        print(f"  {results['calibration_method']}")
    
    # 4. Summary
    print("\n4. SUMMARY")
    print("-" * 80)
    
    print("Cost Calibration (Uncalibrated Brier):")
    for res in cost_cal_results:
        print(f"  {res['model']}: {res['brier_uncalibrated']:.3f}")
    
    print("\nSchedule Calibration (Uncalibrated Brier):")
    for res in schedule_cal_results:
        print(f"  {res['model']}: {res['brier_uncalibrated']:.3f}")
    
    return {
        'cost_cal_results': cost_cal_results,
        'schedule_cal_results': schedule_cal_results
    }


if __name__ == "__main__":
    result = calibration_evaluation()
