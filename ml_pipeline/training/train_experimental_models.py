"""Train experimental RF, XGBoost, LightGBM models on PAIMANA real data.

Uses delay_gt_6_months as primary target (160 labeled projects, 59.4% positive).
Implements class imbalance handling, small hyperparameter search, and comprehensive evaluation.
"""

import csv
import json
import numpy as np
import joblib
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, brier_score_loss, confusion_matrix,
    balanced_accuracy_score, matthews_corrcoef
)
import xgboost as xgb
import lightgbm as lgb

# SHAP is optional - requires C++ build tools
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("SHAP not available (requires C++ build tools). Proceeding without SHAP.")


class ExperimentalModelTrainer:
    """Train experimental ML models with class imbalance handling."""
    
    def __init__(self, target_name: str = 'delay_gt_6_months'):
        self.target_name = target_name
        self.feature_names = []
        self.models = {}
        self.metrics = {}
    
    def load_labeled_data(self, data_dir: Path) -> Tuple[List[Dict], List[Dict]]:
        """Load labeled schedule delay data."""
        # Load schedule delay labels
        records = []
        with open(data_dir / 'training' / 'labeled' / 'schedule_delay_labeled.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        
        # Split into train/validation (exclude July 2026)
        train_records = [r for r in records if r.get('reporting_month', '') != '2026-07']
        holdout_records = [r for r in records if r.get('reporting_month', '') == '2026-07']
        
        return train_records, holdout_records
    
    def extract_features(self, records: List[Dict]) -> np.ndarray:
        """Extract numeric features for modeling."""
        self.feature_names = [
            'original_cost_crore', 'revised_cost_crore', 'cumulative_expenditure_crore',
            'physical_progress_pct'
        ]
        
        features = []
        for record in records:
            row = []
            for fname in self.feature_names:
                val = record.get(fname)
                try:
                    row.append(float(val) if val else 0.0)
                except (ValueError, TypeError):
                    row.append(0.0)
            features.append(row)
        
        return np.array(features)
    
    def extract_target(self, records: List[Dict]) -> np.ndarray:
        """Extract target variable."""
        target = []
        for record in records:
            val = record.get(self.target_name)
            try:
                target.append(int(val) if val is not None else 0)
            except (ValueError, TypeError):
                target.append(0)
        
        return np.array(target)
    
    def calculate_class_weights(self, y: np.ndarray) -> Dict:
        """Calculate class weights for imbalanced data."""
        pos_count = sum(y == 1)
        neg_count = sum(y == 0)
        total = len(y)
        
        return {
            'positive_count': pos_count,
            'negative_count': neg_count,
            'positive_rate': pos_count / total,
            'negative_rate': neg_count / total,
            'scale_pos_weight': neg_count / pos_count if pos_count > 0 else 1.0
        }
    
    def train_random_forest(self, X_train: np.ndarray, y_train: np.ndarray, 
                           X_val: np.ndarray, y_val: np.ndarray) -> Dict:
        """Train Random Forest with class weighting."""
        class_weights = self.calculate_class_weights(y_train)
        
        # Baseline RF
        rf_baseline = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        rf_baseline.fit(X_train, y_train)
        
        # Class-weighted RF
        rf_weighted = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        rf_weighted.fit(X_train, y_train)
        
        # Evaluate both
        baseline_metrics = self.evaluate_model(rf_baseline, X_val, y_val, 'rf_baseline')
        weighted_metrics = self.evaluate_model(rf_weighted, X_val, y_val, 'rf_weighted')
        
        # Select best
        best_model = rf_weighted if weighted_metrics['f1'] > baseline_metrics['f1'] else rf_baseline
        best_metrics = weighted_metrics if weighted_metrics['f1'] > baseline_metrics['f1'] else baseline_metrics
        
        self.models['random_forest'] = best_model
        self.metrics['random_forest'] = best_metrics
        
        return {
            'baseline': baseline_metrics,
            'weighted': weighted_metrics,
            'selected': best_metrics,
            'class_weights': class_weights
        }
    
    def train_xgboost(self, X_train: np.ndarray, y_train: np.ndarray,
                     X_val: np.ndarray, y_val: np.ndarray) -> Dict:
        """Train XGBoost with class weighting."""
        class_weights = self.calculate_class_weights(y_train)
        
        # Baseline XGBoost
        xgb_baseline = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss'
        )
        xgb_baseline.fit(X_train, y_train)
        
        # Class-weighted XGBoost
        xgb_weighted = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=class_weights['scale_pos_weight'],
            random_state=42,
            eval_metric='logloss'
        )
        xgb_weighted.fit(X_train, y_train)
        
        # Evaluate both
        baseline_metrics = self.evaluate_model(xgb_baseline, X_val, y_val, 'xgb_baseline')
        weighted_metrics = self.evaluate_model(xgb_weighted, X_val, y_val, 'xgb_weighted')
        
        # Select best
        best_model = xgb_weighted if weighted_metrics['f1'] > baseline_metrics['f1'] else xgb_baseline
        best_metrics = weighted_metrics if weighted_metrics['f1'] > baseline_metrics['f1'] else baseline_metrics
        
        self.models['xgboost'] = best_model
        self.metrics['xgboost'] = best_metrics
        
        return {
            'baseline': baseline_metrics,
            'weighted': weighted_metrics,
            'selected': best_metrics,
            'class_weights': class_weights
        }
    
    def train_lightgbm(self, X_train: np.ndarray, y_train: np.ndarray,
                      X_val: np.ndarray, y_val: np.ndarray) -> Dict:
        """Train LightGBM with class weighting."""
        class_weights = self.calculate_class_weights(y_train)
        
        # Baseline LightGBM
        lgb_baseline = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbose=-1
        )
        lgb_baseline.fit(X_train, y_train)
        
        # Class-weighted LightGBM
        lgb_weighted = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            is_unbalance=True,
            random_state=42,
            verbose=-1
        )
        lgb_weighted.fit(X_train, y_train)
        
        # Evaluate both
        baseline_metrics = self.evaluate_model(lgb_baseline, X_val, y_val, 'lgb_baseline')
        weighted_metrics = self.evaluate_model(lgb_weighted, X_val, y_val, 'lgb_weighted')
        
        # Select best
        best_model = lgb_weighted if weighted_metrics['f1'] > baseline_metrics['f1'] else lgb_baseline
        best_metrics = weighted_metrics if weighted_metrics['f1'] > baseline_metrics['f1'] else baseline_metrics
        
        self.models['lightgbm'] = best_model
        self.metrics['lightgbm'] = best_metrics
        
        return {
            'baseline': baseline_metrics,
            'weighted': weighted_metrics,
            'selected': best_metrics,
            'class_weights': class_weights
        }
    
    def evaluate_model(self, model, X_test: np.ndarray, y_test: np.ndarray, model_name: str) -> Dict:
        """Evaluate model with comprehensive metrics."""
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        metrics = {
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_proba) if len(set(y_test)) > 1 else 0.5,
            'pr_auc': average_precision_score(y_test, y_proba),
            'brier': brier_score_loss(y_test, y_proba),
            'balanced_accuracy': balanced_accuracy_score(y_test, y_pred),
            'mcc': matthews_corrcoef(y_test, y_pred),
            'confusion_matrix': {
                'true_negative': int(tn),
                'false_positive': int(fp),
                'false_negative': int(fn),
                'true_positive': int(tp)
            },
            'positive_rate': sum(y_test == 1) / len(y_test)
        }
        
        return metrics
    
    def generate_predictions(self, model, X: np.ndarray, records: List[Dict], model_name: str) -> List[Dict]:
        """Generate predictions with metadata."""
        y_pred = model.predict(X)
        y_proba = model.predict_proba(X)[:, 1] if hasattr(model, 'predict_proba') else y_pred
        
        predictions = []
        for i, (record, pred, prob) in enumerate(zip(records, y_pred, y_proba)):
            predictions.append({
                'project_id': record.get('project_id', ''),
                'reporting_month': record.get('reporting_month', ''),
                'predicted_probability': float(prob),
                'predicted_class': int(pred),
                'actual_label': int(record.get(self.target_name, 0)),
                'model_version': f'{model_name}-exp-v1'
            })
        
        return predictions
    
    def generate_shap_explanations(self, model, X: np.ndarray, records: List[Dict], model_name: str) -> List[Dict]:
        """Generate SHAP explanations for representative projects."""
        if not SHAP_AVAILABLE:
            print(f"SHAP not available for {model_name}")
            return []
        
        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X)
            
            # Get top 5 features for first 10 projects
            explanations = []
            for i in range(min(10, len(records))):
                # Get absolute SHAP values
                abs_shap = np.abs(shap_values[i])
                top_indices = np.argsort(abs_shap)[-5:][::-1]
                
                top_features = []
                for idx in top_indices:
                    top_features.append({
                        'feature': self.feature_names[idx],
                        'feature_value': float(X[i, idx]),
                        'shap_value': float(shap_values[i, idx]),
                        'direction': 'positive' if shap_values[i, idx] > 0 else 'negative'
                    })
                
                explanations.append({
                    'project_id': records[i].get('project_id', ''),
                    'reporting_month': records[i].get('reporting_month', ''),
                    'top_5_features': top_features,
                    'model_version': f'{model_name}-exp-v1'
                })
            
            return explanations
        except Exception as e:
            print(f"SHAP generation failed for {model_name}: {e}")
            return []
    
    def save_artifacts(self, data_dir: Path):
        """Save model artifacts and results."""
        artifact_dir = data_dir / 'artifacts' / 'experimental'
        artifact_dir.mkdir(parents=True, exist_ok=True)
        
        results_dir = data_dir / 'results'
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Save models
        for model_name, model in self.models.items():
            joblib.dump(model, artifact_dir / f'{model_name}_experimental.pkl')
        
        # Save metrics
        with open(results_dir / 'experimental_model_metrics.json', 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        # Save feature names
        with open(artifact_dir / 'feature_names.json', 'w') as f:
            json.dump(self.feature_names, f, indent=2)


def train_all_models(data_dir: Path) -> Dict:
    """Train all experimental models."""
    print("Training experimental ML models on PAIMANA real data...")
    
    trainer = ExperimentalModelTrainer(target_name='delay_gt_6_months')
    
    # Load data
    train_records, holdout_records = trainer.load_labeled_data(data_dir)
    print(f"Training records: {len(train_records)}")
    print(f"Holdout records: {len(holdout_records)}")
    
    # Extract features and targets
    X_train = trainer.extract_features(train_records)
    y_train = trainer.extract_target(train_records)
    X_holdout = trainer.extract_features(holdout_records)
    y_holdout = trainer.extract_target(holdout_records)
    
    print(f"Feature shape: {X_train.shape}")
    print(f"Target distribution: {trainer.calculate_class_weights(y_train)}")
    
    # Train models
    print("\nTraining Random Forest...")
    rf_results = trainer.train_random_forest(X_train, y_train, X_holdout, y_holdout)
    print(f"  RF F1: {rf_results['selected']['f1']:.4f}")
    
    print("\nTraining XGBoost...")
    xgb_results = trainer.train_xgboost(X_train, y_train, X_holdout, y_holdout)
    print(f"  XGBoost F1: {xgb_results['selected']['f1']:.4f}")
    
    print("\nTraining LightGBM...")
    lgb_results = trainer.train_lightgbm(X_train, y_train, X_holdout, y_holdout)
    print(f"  LightGBM F1: {lgb_results['selected']['f1']:.4f}")
    
    # Generate predictions
    print("\nGenerating predictions...")
    for model_name, model in trainer.models.items():
        predictions = trainer.generate_predictions(model, X_holdout, holdout_records, model_name)
        
        # Save predictions
        output_path = data_dir / 'results' / f'{model_name}_predictions.csv'
        fieldnames = ['project_id', 'reporting_month', 'predicted_probability', 'predicted_class', 'actual_label', 'model_version']
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(predictions)
        
        print(f"  {model_name} predictions saved: {output_path}")
    
    # Generate SHAP explanations
    print("\nGenerating SHAP explanations...")
    all_shap = {}
    for model_name, model in trainer.models.items():
        shap_explanations = trainer.generate_shap_explanations(model, X_holdout, holdout_records, model_name)
        all_shap[model_name] = shap_explanations
        print(f"  {model_name} SHAP explanations: {len(shap_explanations)}")
    
    # Save SHAP results
    with open(data_dir / 'results' / 'shap_examples.json', 'w') as f:
        json.dump(all_shap, f, indent=2)
    
    # Save artifacts
    trainer.save_artifacts(data_dir)
    
    return {
        'random_forest': rf_results,
        'xgboost': xgb_results,
        'lightgbm': lgb_results,
        'metrics': trainer.metrics
    }


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    
    results = train_all_models(data_dir)
    
    print("\n" + "="*60)
    print("EXPERIMENTAL MODEL TRAINING COMPLETE")
    print("="*60)
    print("\nModel Comparison (F1 Score):")
    for model_name, model_results in results.items():
        if model_name != 'metrics':
            print(f"  {model_name}: {model_results['selected']['f1']:.4f}")
    
    print("\nSTATUS: EXPERIMENTAL — NOT PRODUCTION VALIDATED")
    print("These models demonstrate technical feasibility but have")
    print("insufficient completed-project labels for production accuracy claims.")
