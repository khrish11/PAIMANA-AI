"""SHAP analysis for v2 models using TreeExplainer."""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
import shap


def generate_shap_analysis(model, X_val, feature_names, model_name):
    """Generate SHAP analysis for a model."""
    print(f"\nGenerating SHAP analysis for {model_name}...")
    
    try:
        # Create TreeExplainer
        explainer = shap.TreeExplainer(model)
        
        # Calculate SHAP values
        shap_values = explainer.shap_values(X_val)
        
        # If shap_values is a list (for multi-class), take the first class
        if isinstance(shap_values, list):
            shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
        
        # Mean absolute SHAP values (global feature importance)
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        
        # Get top 10 features
        top_indices = np.argsort(mean_abs_shap)[::-1][:10]
        
        top_features = []
        for idx in top_indices:
            top_features.append({
                'feature': feature_names[idx],
                'mean_abs_shap': mean_abs_shap[idx]
            })
        
        print(f"  Top 10 features by mean absolute SHAP:")
        for feat in top_features:
            print(f"    {feat['feature']}: {feat['mean_abs_shap']:.4f}")
        
        # Sample local explanations (5 projects)
        sample_indices = np.random.choice(len(X_val), min(5, len(X_val)), replace=False)
        
        local_explanations = []
        for idx in sample_indices:
            shap_vals = shap_values[idx]
            top_local_indices = np.argsort(np.abs(shap_vals))[::-1][:5]
            
            local_explanations.append({
                'sample_index': idx,
                'top_features': [
                    {
                        'feature': feature_names[i],
                        'shap_value': shap_vals[i]
                    }
                    for i in top_local_indices
                ]
            })
        
        return {
            'model': model_name,
            'top_features': top_features,
            'local_explanations': local_explanations,
            'shap_values': shap_values
        }
        
    except Exception as e:
        print(f"  Error generating SHAP for {model_name}: {e}")
        return {
            'model': model_name,
            'error': str(e),
            'top_features': [],
            'local_explanations': []
        }


def shap_analysis():
    """Generate SHAP analysis for all v2 models."""
    print("=" * 80)
    print("SHAP ANALYSIS V2")
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
    
    with open(data_dir / 'cost_feature_names.json', 'r') as f:
        cost_feature_names = json.load(f)
    
    X_cost_val = X_cost_val[cost_feature_names].fillna(0)
    
    # Load schedule data
    X_schedule_val = pd.read_csv(data_dir / 'schedule_delay_val_features.csv')
    
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
    
    # 2. Cost SHAP analysis
    print("\n2. COST SHAP ANALYSIS")
    print("-" * 80)
    
    cost_shap_results = []
    for model, name in [(rf_cost, "Random Forest"), (xgb_cost, "XGBoost"), (lgb_cost, "LightGBM")]:
        results = generate_shap_analysis(model, X_cost_val.values, cost_feature_names, name)
        cost_shap_results.append(results)
    
    # 3. Schedule SHAP analysis
    print("\n3. SCHEDULE SHAP ANALYSIS")
    print("-" * 80)
    
    schedule_shap_results = []
    for model, name in [(rf_schedule, "Random Forest"), (xgb_schedule, "XGBoost"), (lgb_schedule, "LightGBM")]:
        results = generate_shap_analysis(model, X_schedule_val.values, schedule_feature_names, name)
        schedule_shap_results.append(results)
    
    # 4. Save SHAP results
    print("\n4. SAVING SHAP RESULTS")
    print("-" * 80)
    
    output_dir = Path('../data/artifacts/experimental/v2')
    if not output_dir.exists():
        output_dir = Path('data/artifacts/experimental/v2')
    
    # Save as JSON
    shap_summary = {
        'cost_shap': cost_shap_results,
        'schedule_shap': schedule_shap_results
    }
    
    with open(output_dir / 'shap_summary_v2.json', 'w') as f:
        json.dump(shap_summary, f, indent=2, default=str)
    
    print(f"Saved SHAP summary to {output_dir / 'shap_summary_v2.json'}")
    
    # 5. Summary
    print("\n5. SUMMARY")
    print("-" * 80)
    
    print("Cost SHAP - Top features by model:")
    for res in cost_shap_results:
        if 'error' not in res:
            print(f"  {res['model']}:")
            for feat in res['top_features'][:3]:
                print(f"    {feat['feature']}: {feat['mean_abs_shap']:.4f}")
    
    print("\nSchedule SHAP - Top features by model:")
    for res in schedule_shap_results:
        if 'error' not in res:
            print(f"  {res['model']}:")
            for feat in res['top_features'][:3]:
                print(f"    {feat['feature']}: {feat['mean_abs_shap']:.4f}")
    
    return shap_summary


if __name__ == "__main__":
    result = shap_analysis()
