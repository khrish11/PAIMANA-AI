"""Baseline comparison for v2 models."""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
from sklearn.metrics import (
    precision_score, recall_score, f1_score, 
    roc_auc_score, average_precision_score, brier_score_loss,
    matthews_corrcoef, balanced_accuracy_score
)
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.linear_model import LogisticRegression


def evaluate_baseline(y_true, y_pred, y_proba, model_name):
    """Evaluate baseline model."""
    metrics = {
        'model': model_name,
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_true, y_proba) if len(np.unique(y_true)) > 1 else 0,
        'pr_auc': average_precision_score(y_true, y_proba) if len(np.unique(y_true)) > 1 else 0,
        'brier': brier_score_loss(y_true, y_proba),
        'mcc': matthews_corrcoef(y_true, y_pred),
        'balanced_accuracy': balanced_accuracy_score(y_true, y_pred)
    }
    return metrics


def baseline_comparison():
    """Compare tree models against baselines."""
    print("=" * 80)
    print("BASELINE COMPARISON V2")
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
    X_cost_train = pd.read_csv(data_dir / 'cost_overrun_train_features.csv')
    y_cost_train = X_cost_train['cost_overrun_10pct']
    X_cost_val = pd.read_csv(data_dir / 'cost_overrun_val_features.csv')
    y_cost_val = X_cost_val['cost_overrun_10pct']
    
    with open(data_dir / 'cost_feature_names.json', 'r') as f:
        cost_feature_names = json.load(f)
    
    X_cost_train = X_cost_train[cost_feature_names].fillna(0)
    X_cost_val = X_cost_val[cost_feature_names].fillna(0)
    
    # Load schedule data
    X_schedule_train = pd.read_csv(data_dir / 'schedule_delay_train_features.csv')
    y_schedule_train = X_schedule_train['delay_gt_6_months']
    X_schedule_val = pd.read_csv(data_dir / 'schedule_delay_val_features.csv')
    y_schedule_val = X_schedule_val['delay_gt_6_months']
    
    with open(data_dir / 'schedule_feature_names.json', 'r') as f:
        schedule_feature_names = json.load(f)
    
    X_schedule_train = X_schedule_train[schedule_feature_names].fillna(0)
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
    
    # 2. Cost baselines
    print("\n2. COST BASELINES")
    print("-" * 80)
    
    cost_results = []
    
    # Majority classifier
    majority = DummyClassifier(strategy='most_frequent', random_state=42)
    majority.fit(X_cost_train, y_cost_train)
    y_pred = majority.predict(X_cost_val)
    y_proba = majority.predict_proba(X_cost_val)[:, 1]
    cost_results.append(evaluate_baseline(y_cost_val, y_pred, y_proba, "Majority"))
    
    # Stratified dummy
    stratified = DummyClassifier(strategy='stratified', random_state=42)
    stratified.fit(X_cost_train, y_cost_train)
    y_pred = stratified.predict(X_cost_val)
    y_proba = stratified.predict_proba(X_cost_val)[:, 1]
    cost_results.append(evaluate_baseline(y_cost_val, y_pred, y_proba, "Stratified"))
    
    # Logistic regression
    logreg = LogisticRegression(max_iter=1000, random_state=42)
    logreg.fit(X_cost_train, y_cost_train)
    y_pred = logreg.predict(X_cost_val)
    y_proba = logreg.predict_proba(X_cost_val)[:, 1]
    cost_results.append(evaluate_baseline(y_cost_val, y_pred, y_proba, "Logistic Regression"))
    
    # Tree models
    for model, name in [(rf_cost, "Random Forest"), (xgb_cost, "XGBoost"), (lgb_cost, "LightGBM")]:
        y_pred = model.predict(X_cost_val)
        y_proba = model.predict_proba(X_cost_val)[:, 1]
        cost_results.append(evaluate_baseline(y_cost_val, y_pred, y_proba, name))
    
    # 3. Schedule baselines
    print("\n3. SCHEDULE BASELINES")
    print("-" * 80)
    
    schedule_results = []
    
    # Majority classifier
    majority = DummyClassifier(strategy='most_frequent', random_state=42)
    majority.fit(X_schedule_train, y_schedule_train)
    y_pred = majority.predict(X_schedule_val)
    y_proba = majority.predict_proba(X_schedule_val)[:, 1]
    schedule_results.append(evaluate_baseline(y_schedule_val, y_pred, y_proba, "Majority"))
    
    # Stratified dummy
    stratified = DummyClassifier(strategy='stratified', random_state=42)
    stratified.fit(X_schedule_train, y_schedule_train)
    y_pred = stratified.predict(X_schedule_val)
    y_proba = stratified.predict_proba(X_schedule_val)[:, 1]
    schedule_results.append(evaluate_baseline(y_schedule_val, y_pred, y_proba, "Stratified"))
    
    # Logistic regression
    logreg = LogisticRegression(max_iter=1000, random_state=42)
    logreg.fit(X_schedule_train, y_schedule_train)
    y_pred = logreg.predict(X_schedule_val)
    y_proba = logreg.predict_proba(X_schedule_val)[:, 1]
    schedule_results.append(evaluate_baseline(y_schedule_val, y_pred, y_proba, "Logistic Regression"))
    
    # Tree models
    for model, name in [(rf_schedule, "Random Forest"), (xgb_schedule, "XGBoost"), (lgb_schedule, "LightGBM")]:
        y_pred = model.predict(X_schedule_val)
        y_proba = model.predict_proba(X_schedule_val)[:, 1]
        schedule_results.append(evaluate_baseline(y_schedule_val, y_pred, y_proba, name))
    
    # 4. Display results
    print("\n4. COST RESULTS")
    print("-" * 80)
    cost_df = pd.DataFrame(cost_results)
    print(cost_df.round(3))
    
    print("\n5. SCHEDULE RESULTS")
    print("-" * 80)
    schedule_df = pd.DataFrame(schedule_results)
    print(schedule_df.round(3))
    
    # 6. Summary
    print("\n6. SUMMARY")
    print("-" * 80)
    
    print("Cost Overrun - Best by ROC-AUC:")
    best_cost = cost_df.loc[cost_df['roc_auc'].idxmax()]
    print(f"  {best_cost['model']}: ROC-AUC = {best_cost['roc_auc']:.3f}")
    
    print("\nSchedule Delay - Best by ROC-AUC:")
    best_schedule = schedule_df.loc[schedule_df['roc_auc'].idxmax()]
    print(f"  {best_schedule['model']}: ROC-AUC = {best_schedule['roc_auc']:.3f}")
    
    print("\nImprovement over baselines:")
    cost_baseline_roc = cost_df[cost_df['model'] == 'Majority']['roc_auc'].values[0]
    schedule_baseline_roc = schedule_df[schedule_df['model'] == 'Majority']['roc_auc'].values[0]
    
    print(f"  Cost: {best_cost['roc_auc']:.3f} vs baseline {cost_baseline_roc:.3f}")
    print(f"  Schedule: {best_schedule['roc_auc']:.3f} vs baseline {schedule_baseline_roc:.3f}")
    
    return {
        'cost_results': cost_results,
        'schedule_results': schedule_results
    }


if __name__ == "__main__":
    result = baseline_comparison()
