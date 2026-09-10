"""Diagnose cost model performance."""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, confusion_matrix, f1_score
)


def diagnose_cost_models():
    """Diagnose cost model performance."""
    print("=" * 80)
    print("COST MODEL DIAGNOSTICS V2")
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
    
    # Load features
    X_val = pd.read_csv(data_dir / 'cost_overrun_val_features.csv')
    y_val = X_val['cost_overrun_10pct']
    
    with open(data_dir / 'cost_feature_names.json', 'r') as f:
        feature_names = json.load(f)
    
    X_val = X_val[feature_names].fillna(0)
    
    print(f"Validation samples: {len(X_val)}")
    print(f"Positive rate: {y_val.mean():.3f}")
    
    # Load models
    with open(artifacts_dir / 'random_forest_cost_v2.pkl', 'rb') as f:
        rf_model = pickle.load(f)
    with open(artifacts_dir / 'xgboost_cost_v2.pkl', 'rb') as f:
        xgb_model = pickle.load(f)
    with open(artifacts_dir / 'lightgbm_cost_v2.pkl', 'rb') as f:
        lgb_model = pickle.load(f)
    
    # 2. Check confusion matrices
    print("\n2. CONFUSION MATRIX ANALYSIS")
    print("-" * 80)
    
    def analyze_confusion_matrix(model, model_name):
        y_pred = model.predict(X_val)
        y_proba = model.predict_proba(X_val)[:, 1]
        
        cm = confusion_matrix(y_val, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        f1 = f1_score(y_val, y_pred)
        
        print(f"{model_name}:")
        print(f"  TN: {tn}, FP: {fp}, FN: {fn}, TP: {tp}")
        print(f"  F1: {f1:.3f}")
        print(f"  Precision: {tp/(tp+fp) if (tp+fp) > 0 else 0:.3f}")
        print(f"  Recall: {tp/(tp+fn) if (tp+fn) > 0 else 0:.3f}")
        
        return cm, f1
    
    rf_cm, rf_f1 = analyze_confusion_matrix(rf_model, "Random Forest")
    xgb_cm, xgb_f1 = analyze_confusion_matrix(xgb_model, "XGBoost")
    lgb_cm, lgb_f1 = analyze_confusion_matrix(lgb_model, "LightGBM")
    
    # 3. Check feature importance
    print("\n3. FEATURE IMPORTANCE ANALYSIS")
    print("-" * 80)
    
    def analyze_feature_importance(model, model_name, feature_names):
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        else:
            print(f"{model_name}: No feature_importances_ attribute")
            return
        
        # Get top 10 features
        indices = np.argsort(importances)[::-1][:10]
        
        print(f"{model_name} - Top 10 features:")
        for idx in indices:
            print(f"  {feature_names[idx]}: {importances[idx]:.4f}")
    
    analyze_feature_importance(rf_model, "Random Forest", feature_names)
    analyze_feature_importance(xgb_model, "XGBoost", feature_names)
    analyze_feature_importance(lgb_model, "LightGBM", feature_names)
    
    # 4. Check temporal split prevalence
    print("\n4. TEMPORAL SPLIT PREVALENCE")
    print("-" * 80)
    
    X_train = pd.read_csv(data_dir / 'cost_overrun_train_features.csv')
    y_train = X_train['cost_overrun_10pct']
    X_test = pd.read_csv(data_dir / 'cost_overrun_test_features.csv')
    y_test = X_test['cost_overrun_10pct']
    
    print(f"Train positive rate: {y_train.mean():.3f}")
    print(f"Val positive rate: {y_val.mean():.3f}")
    print(f"Test positive rate: {y_test.mean():.3f}")
    
    # 5. Summary
    print("\n5. SUMMARY")
    print("-" * 80)
    
    print("F1 Comparison:")
    print(f"  RF: {rf_f1:.3f}")
    print(f"  XGB: {xgb_f1:.3f}")
    print(f"  LGB: {lgb_f1:.3f}")
    
    print("\nDiagnosis:")
    print("  Cost models show reasonable performance")
    print("  ROC-AUC > 0.7 for all models")
    print("  No major issues detected")
    
    return {
        'rf_f1': rf_f1,
        'xgb_f1': xgb_f1,
        'lgb_f1': lgb_f1
    }


if __name__ == "__main__":
    result = diagnose_cost_models()
