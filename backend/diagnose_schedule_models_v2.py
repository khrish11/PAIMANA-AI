"""Diagnose schedule model ROC-AUC < 0.5 issue."""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, roc_curve,
    confusion_matrix, f1_score
)


def diagnose_schedule_models():
    """Diagnose schedule model performance issues."""
    print("=" * 80)
    print("SCHEDULE MODEL DIAGNOSTICS V2")
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
    X_val = pd.read_csv(data_dir / 'schedule_delay_val_features.csv')
    y_val = X_val['delay_gt_6_months']
    
    with open(data_dir / 'schedule_feature_names.json', 'r') as f:
        feature_names = json.load(f)
    
    X_val = X_val[feature_names].fillna(0)
    
    print(f"Validation samples: {len(X_val)}")
    print(f"Positive rate: {y_val.mean():.3f}")
    
    # Load models
    with open(artifacts_dir / 'random_forest_schedule_v2.pkl', 'rb') as f:
        rf_model = pickle.load(f)
    with open(artifacts_dir / 'xgboost_schedule_v2.pkl', 'rb') as f:
        xgb_model = pickle.load(f)
    with open(artifacts_dir / 'lightgbm_schedule_v2.pkl', 'rb') as f:
        lgb_model = pickle.load(f)
    
    # 2. Check target inversion
    print("\n2. TARGET INVERSION DIAGNOSTIC")
    print("-" * 80)
    
    def check_inversion(model, model_name):
        y_proba = model.predict_proba(X_val)[:, 1]
        
        # Original ROC-AUC
        roc_auc_original = roc_auc_score(y_val, y_proba)
        
        # Inverted ROC-AUC
        roc_auc_inverted = roc_auc_score(y_val, 1 - y_proba)
        
        print(f"{model_name}:")
        print(f"  ROC-AUC (original): {roc_auc_original:.3f}")
        print(f"  ROC-AUC (inverted): {roc_auc_inverted:.3f}")
        
        if roc_auc_inverted > roc_auc_original:
            print(f"  ⚠️ Inverted ROC-AUC is higher - possible label/probability inversion")
        
        return roc_auc_original, roc_auc_inverted
    
    rf_roc, rf_roc_inv = check_inversion(rf_model, "Random Forest")
    xgb_roc, xgb_roc_inv = check_inversion(xgb_model, "XGBoost")
    lgb_roc, lgb_roc_inv = check_inversion(lgb_model, "LightGBM")
    
    # 3. Check confusion matrices
    print("\n3. CONFUSION MATRIX ANALYSIS")
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
    
    # 4. Check threshold vs ranking
    print("\n4. THRESHOLD VS RANKING ANALYSIS")
    print("-" * 80)
    
    def analyze_threshold_sweep(model, model_name):
        y_proba = model.predict_proba(X_val)[:, 1]
        
        thresholds = np.arange(0.1, 0.9, 0.1)
        f1_scores = []
        
        for thresh in thresholds:
            y_pred = (y_proba >= thresh).astype(int)
            f1 = f1_score(y_val, y_pred, zero_division=0)
            f1_scores.append(f1)
        
        print(f"{model_name}:")
        for thresh, f1 in zip(thresholds, f1_scores):
            print(f"  Threshold {thresh:.1f}: F1 = {f1:.3f}")
        
        return f1_scores
    
    rf_f1_sweep = analyze_threshold_sweep(rf_model, "Random Forest")
    xgb_f1_sweep = analyze_threshold_sweep(xgb_model, "XGBoost")
    lgb_f1_sweep = analyze_threshold_sweep(lgb_model, "LightGBM")
    
    # 5. Check feature importance
    print("\n5. FEATURE IMPORTANCE ANALYSIS")
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
    
    # 6. Check temporal split prevalence
    print("\n6. TEMPORAL SPLIT PREVALENCE")
    print("-" * 80)
    
    X_train = pd.read_csv(data_dir / 'schedule_delay_train_features.csv')
    y_train = X_train['delay_gt_6_months']
    X_test = pd.read_csv(data_dir / 'schedule_delay_test_features.csv')
    y_test = X_test['delay_gt_6_months']
    
    print(f"Train positive rate: {y_train.mean():.3f}")
    print(f"Val positive rate: {y_val.mean():.3f}")
    print(f"Test positive rate: {y_test.mean():.3f}")
    
    # 7. Summary
    print("\n7. SUMMARY")
    print("-" * 80)
    
    print("ROC-AUC Comparison:")
    print(f"  RF: {rf_roc:.3f} (inverted: {rf_roc_inv:.3f})")
    print(f"  XGB: {xgb_roc:.3f} (inverted: {xgb_roc_inv:.3f})")
    print(f"  LGB: {lgb_roc:.3f} (inverted: {lgb_roc_inv:.3f})")
    
    print("\nF1 Comparison:")
    print(f"  RF: {rf_f1:.3f}")
    print(f"  XGB: {xgb_f1:.3f}")
    print(f"  LGB: {lgb_f1:.3f}")
    
    print("\nDiagnosis:")
    if all([rf_roc < 0.5, xgb_roc < 0.5, lgb_roc < 0.5]):
        print("  ⚠️ ALL models have ROC-AUC < 0.5")
        print("  This suggests a fundamental issue with:")
        print("  - Target definition")
        print("  - Feature construction")
        print("  - Data quality")
    elif any([rf_roc_inv > 0.5, xgb_roc_inv > 0.5, lgb_roc_inv > 0.5]):
        print("  ⚠️ Inverted ROC-AUC > 0.5 for some models")
        print("  This suggests probability/class label inversion")
    else:
        print("  Some models have ROC-AUC > 0.5")
        print("  Issue may be model-specific")
    
    return {
        'rf_roc': rf_roc,
        'rf_roc_inv': rf_roc_inv,
        'xgb_roc': xgb_roc,
        'xgb_roc_inv': xgb_roc_inv,
        'lgb_roc': lgb_roc,
        'lgb_roc_inv': lgb_roc_inv,
        'rf_f1': rf_f1,
        'xgb_f1': xgb_f1,
        'lgb_f1': lgb_f1
    }


if __name__ == "__main__":
    result = diagnose_schedule_models()
