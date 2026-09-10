"""Train v2 ML models using 454 completed projects."""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, 
    roc_auc_score, average_precision_score, brier_score_loss,
    matthews_corrcoef, balanced_accuracy_score, confusion_matrix
)
import warnings
warnings.filterwarnings('ignore')


def train_random_forest(X_train, y_train, X_val, y_val, target_name):
    """Train Random Forest classifier."""
    print(f"\nTraining Random Forest for {target_name}...")
    
    # Calculate class weights for imbalance
    pos_count = y_train.sum()
    neg_count = len(y_train) - pos_count
    class_weight = 'balanced' if pos_count / len(y_train) < 0.3 or pos_count / len(y_train) > 0.7 else None
    
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight=class_weight,
        random_state=42,
        n_jobs=-1
    )
    
    rf.fit(X_train, y_train)
    
    # Predictions
    y_pred_train = rf.predict(X_train)
    y_pred_val = rf.predict(X_val)
    y_proba_val = rf.predict_proba(X_val)[:, 1]
    
    # Metrics
    metrics = {
        'train_precision': precision_score(y_train, y_pred_train, zero_division=0),
        'train_recall': recall_score(y_train, y_pred_train, zero_division=0),
        'train_f1': f1_score(y_train, y_pred_train, zero_division=0),
        'val_precision': precision_score(y_val, y_pred_val, zero_division=0),
        'val_recall': recall_score(y_val, y_pred_val, zero_division=0),
        'val_f1': f1_score(y_val, y_pred_val, zero_division=0),
        'val_roc_auc': roc_auc_score(y_val, y_proba_val) if len(np.unique(y_val)) > 1 else 0,
        'val_pr_auc': average_precision_score(y_val, y_proba_val) if len(np.unique(y_val)) > 1 else 0,
        'val_brier': brier_score_loss(y_val, y_proba_val),
        'val_mcc': matthews_corrcoef(y_val, y_pred_val),
        'val_balanced_accuracy': balanced_accuracy_score(y_val, y_pred_val)
    }
    
    # Confusion matrix
    cm = confusion_matrix(y_val, y_pred_val)
    
    print(f"  Train F1: {metrics['train_f1']:.3f}")
    print(f"  Val F1: {metrics['val_f1']:.3f}")
    print(f"  Val ROC-AUC: {metrics['val_roc_auc']:.3f}")
    print(f"  Val PR-AUC: {metrics['val_pr_auc']:.3f}")
    
    return rf, metrics, cm


def train_xgboost(X_train, y_train, X_val, y_val, target_name):
    """Train XGBoost classifier."""
    print(f"\nTraining XGBoost for {target_name}...")
    
    try:
        import xgboost as xgb
    except ImportError:
        print("  XGBoost not installed, skipping")
        return None, None, None
    
    # Calculate scale_pos_weight for imbalance
    pos_count = y_train.sum()
    neg_count = len(y_train) - pos_count
    scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1
    
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight if pos_count / len(y_train) < 0.3 or pos_count / len(y_train) > 0.7 else 1,
        random_state=42,
        n_jobs=-1,
        eval_metric='logloss'
    )
    
    xgb_model.fit(X_train, y_train)
    
    # Predictions
    y_pred_train = xgb_model.predict(X_train)
    y_pred_val = xgb_model.predict(X_val)
    y_proba_val = xgb_model.predict_proba(X_val)[:, 1]
    
    # Metrics
    metrics = {
        'train_precision': precision_score(y_train, y_pred_train, zero_division=0),
        'train_recall': recall_score(y_train, y_pred_train, zero_division=0),
        'train_f1': f1_score(y_train, y_pred_train, zero_division=0),
        'val_precision': precision_score(y_val, y_pred_val, zero_division=0),
        'val_recall': recall_score(y_val, y_pred_val, zero_division=0),
        'val_f1': f1_score(y_val, y_pred_val, zero_division=0),
        'val_roc_auc': roc_auc_score(y_val, y_proba_val) if len(np.unique(y_val)) > 1 else 0,
        'val_pr_auc': average_precision_score(y_val, y_proba_val) if len(np.unique(y_val)) > 1 else 0,
        'val_brier': brier_score_loss(y_val, y_proba_val),
        'val_mcc': matthews_corrcoef(y_val, y_pred_val),
        'val_balanced_accuracy': balanced_accuracy_score(y_val, y_pred_val)
    }
    
    # Confusion matrix
    cm = confusion_matrix(y_val, y_pred_val)
    
    print(f"  Train F1: {metrics['train_f1']:.3f}")
    print(f"  Val F1: {metrics['val_f1']:.3f}")
    print(f"  Val ROC-AUC: {metrics['val_roc_auc']:.3f}")
    print(f"  Val PR-AUC: {metrics['val_pr_auc']:.3f}")
    
    return xgb_model, metrics, cm


def train_lightgbm(X_train, y_train, X_val, y_val, target_name):
    """Train LightGBM classifier."""
    print(f"\nTraining LightGBM for {target_name}...")
    
    try:
        import lightgbm as lgb
        print(f"  LightGBM version: {lgb.__version__}")
    except ImportError as e:
        print(f"  LightGBM not installed: {e}")
        return None, None, None
    except Exception as e:
        print(f"  LightGBM import error: {e}")
        return None, None, None
    
    # Calculate scale_pos_weight for imbalance
    pos_count = y_train.sum()
    neg_count = len(y_train) - pos_count
    scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1
    
    try:
        lgb_model = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=scale_pos_weight if pos_count / len(y_train) < 0.3 or pos_count / len(y_train) > 0.7 else 1,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
        
        lgb_model.fit(X_train, y_train)
        
        # Predictions
        y_pred_train = lgb_model.predict(X_train)
        y_pred_val = lgb_model.predict(X_val)
        y_proba_val = lgb_model.predict_proba(X_val)[:, 1]
        
        # Metrics
        metrics = {
            'train_precision': precision_score(y_train, y_pred_train, zero_division=0),
            'train_recall': recall_score(y_train, y_pred_train, zero_division=0),
            'train_f1': f1_score(y_train, y_pred_train, zero_division=0),
            'val_precision': precision_score(y_val, y_pred_val, zero_division=0),
            'val_recall': recall_score(y_val, y_pred_val, zero_division=0),
            'val_f1': f1_score(y_val, y_pred_val, zero_division=0),
            'val_roc_auc': roc_auc_score(y_val, y_proba_val) if len(np.unique(y_val)) > 1 else 0,
            'val_pr_auc': average_precision_score(y_val, y_proba_val) if len(np.unique(y_val)) > 1 else 0,
            'val_brier': brier_score_loss(y_val, y_proba_val),
            'val_mcc': matthews_corrcoef(y_val, y_pred_val),
            'val_balanced_accuracy': balanced_accuracy_score(y_val, y_pred_val)
        }
        
        # Confusion matrix
        cm = confusion_matrix(y_val, y_pred_val)
        
        print(f"  Train F1: {metrics['train_f1']:.3f}")
        print(f"  Val F1: {metrics['val_f1']:.3f}")
        print(f"  Val ROC-AUC: {metrics['val_roc_auc']:.3f}")
        print(f"  Val PR-AUC: {metrics['val_pr_auc']:.3f}")
        
        return lgb_model, metrics, cm
        
    except Exception as e:
        print(f"  LightGBM training error: {e}")
        return None, None, None


def train_v2_models():
    """Train all v2 models."""
    print("=" * 80)
    print("TRAINING V2 ML MODELS")
    print("=" * 80)
    
    # 1. Load feature datasets
    print("\n1. LOADING FEATURE DATASETS")
    print("-" * 80)
    
    data_dir = Path('../data/training/v2')
    if not data_dir.exists():
        data_dir = Path('data/training/v2')
    
    # Load cost features
    cost_train = pd.read_csv(data_dir / 'cost_overrun_train_features.csv')
    cost_val = pd.read_csv(data_dir / 'cost_overrun_val_features.csv')
    cost_test = pd.read_csv(data_dir / 'cost_overrun_test_features.csv')
    
    with open(data_dir / 'cost_feature_names.json', 'r') as f:
        cost_feature_names = json.load(f)
    
    # Load schedule features
    schedule_train = pd.read_csv(data_dir / 'schedule_delay_train_features.csv')
    schedule_val = pd.read_csv(data_dir / 'schedule_delay_val_features.csv')
    schedule_test = pd.read_csv(data_dir / 'schedule_delay_test_features.csv')
    
    with open(data_dir / 'schedule_feature_names.json', 'r') as f:
        schedule_feature_names = json.load(f)
    
    print(f"Cost train: {len(cost_train)}, features: {len(cost_feature_names)}")
    print(f"Schedule train: {len(schedule_train)}, features: {len(schedule_feature_names)}")
    
    # 2. Train cost overrun models
    print("\n2. TRAINING COST OVERRUN MODELS")
    print("-" * 80)
    
    # Use delay_gt_6_months as primary target (most balanced)
    cost_target = 'cost_overrun_10pct'
    
    X_cost_train = cost_train[cost_feature_names].fillna(0)
    y_cost_train = cost_train[cost_target]
    X_cost_val = cost_val[cost_feature_names].fillna(0)
    y_cost_val = cost_val[cost_target]
    
    print(f"Target: {cost_target}")
    print(f"Positive rate: {y_cost_train.mean():.3f}")
    
    rf_cost, rf_cost_metrics, rf_cost_cm = train_random_forest(
        X_cost_train, y_cost_train, X_cost_val, y_cost_val, 'cost_overrun'
    )
    
    xgb_cost, xgb_cost_metrics, xgb_cost_cm = train_xgboost(
        X_cost_train, y_cost_train, X_cost_val, y_cost_val, 'cost_overrun'
    )
    
    lgb_cost, lgb_cost_metrics, lgb_cost_cm = train_lightgbm(
        X_cost_train, y_cost_train, X_cost_val, y_cost_val, 'cost_overrun'
    )
    
    # 3. Train schedule delay models
    print("\n3. TRAINING SCHEDULE DELAY MODELS")
    print("-" * 80)
    
    schedule_target = 'delay_gt_6_months'
    
    X_schedule_train = schedule_train[schedule_feature_names].fillna(0)
    y_schedule_train = schedule_train[schedule_target]
    X_schedule_val = schedule_val[schedule_feature_names].fillna(0)
    y_schedule_val = schedule_val[schedule_target]
    
    print(f"Target: {schedule_target}")
    print(f"Positive rate: {y_schedule_train.mean():.3f}")
    
    rf_schedule, rf_schedule_metrics, rf_schedule_cm = train_random_forest(
        X_schedule_train, y_schedule_train, X_schedule_val, y_schedule_val, 'schedule_delay'
    )
    
    xgb_schedule, xgb_schedule_metrics, xgb_schedule_cm = train_xgboost(
        X_schedule_train, y_schedule_train, X_schedule_val, y_schedule_val, 'schedule_delay'
    )
    
    lgb_schedule, lgb_schedule_metrics, lgb_schedule_cm = train_lightgbm(
        X_schedule_train, y_schedule_train, X_schedule_val, y_schedule_val, 'schedule_delay'
    )
    
    # 4. Save models
    print("\n4. SAVING MODELS")
    print("-" * 80)
    
    artifacts_dir = Path('../data/artifacts/experimental/v2')
    if not artifacts_dir.parent.exists():
        artifacts_dir = Path('data/artifacts/experimental/v2')
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Save cost models
    if rf_cost:
        with open(artifacts_dir / 'random_forest_cost_v2.pkl', 'wb') as f:
            pickle.dump(rf_cost, f)
    if xgb_cost:
        with open(artifacts_dir / 'xgboost_cost_v2.pkl', 'wb') as f:
            pickle.dump(xgb_cost, f)
    if lgb_cost:
        with open(artifacts_dir / 'lightgbm_cost_v2.pkl', 'wb') as f:
            pickle.dump(lgb_cost, f)
    
    # Save schedule models
    if rf_schedule:
        with open(artifacts_dir / 'random_forest_schedule_v2.pkl', 'wb') as f:
            pickle.dump(rf_schedule, f)
    if xgb_schedule:
        with open(artifacts_dir / 'xgboost_schedule_v2.pkl', 'wb') as f:
            pickle.dump(xgb_schedule, f)
    if lgb_schedule:
        with open(artifacts_dir / 'lightgbm_schedule_v2.pkl', 'wb') as f:
            pickle.dump(lgb_schedule, f)
    
    # Save feature names
    with open(artifacts_dir / 'cost_feature_names_v2.json', 'w') as f:
        json.dump(cost_feature_names, f)
    with open(artifacts_dir / 'schedule_feature_names_v2.json', 'w') as f:
        json.dump(schedule_feature_names, f)
    
    print(f"Saved models to {artifacts_dir}")
    
    # 5. Summary
    print("\n5. SUMMARY")
    print("-" * 80)
    
    results = {
        'cost_overrun': {
            'random_forest': rf_cost_metrics if rf_cost else None,
            'xgboost': xgb_cost_metrics if xgb_cost else None,
            'lightgbm': lgb_cost_metrics if lgb_cost else None,
            'lightgbm_available': lgb_cost is not None
        },
        'schedule_delay': {
            'random_forest': rf_schedule_metrics if rf_schedule else None,
            'xgboost': xgb_schedule_metrics if xgb_schedule else None,
            'lightgbm': lgb_schedule_metrics if lgb_schedule else None,
            'lightgbm_available': lgb_schedule is not None
        }
    }
    
    print(f"\nCost Overrun (target: {cost_target}):")
    if rf_cost_metrics:
        print(f"  RF Val F1: {rf_cost_metrics['val_f1']:.3f}, ROC-AUC: {rf_cost_metrics['val_roc_auc']:.3f}")
    if xgb_cost_metrics:
        print(f"  XGB Val F1: {xgb_cost_metrics['val_f1']:.3f}, ROC-AUC: {xgb_cost_metrics['val_roc_auc']:.3f}")
    if lgb_cost_metrics:
        print(f"  LGB Val F1: {lgb_cost_metrics['val_f1']:.3f}, ROC-AUC: {lgb_cost_metrics['val_roc_auc']:.3f}")
    else:
        print(f"  LGB: UNAVAILABLE")
    
    print(f"\nSchedule Delay (target: {schedule_target}):")
    if rf_schedule_metrics:
        print(f"  RF Val F1: {rf_schedule_metrics['val_f1']:.3f}, ROC-AUC: {rf_schedule_metrics['val_roc_auc']:.3f}")
    if xgb_schedule_metrics:
        print(f"  XGB Val F1: {xgb_schedule_metrics['val_f1']:.3f}, ROC-AUC: {xgb_schedule_metrics['val_roc_auc']:.3f}")
    if lgb_schedule_metrics:
        print(f"  LGB Val F1: {lgb_schedule_metrics['val_f1']:.3f}, ROC-AUC: {lgb_schedule_metrics['val_roc_auc']:.3f}")
    else:
        print(f"  LGB: UNAVAILABLE")
    
    return results


if __name__ == "__main__":
    results = train_v2_models()
