"""Compare experimental ML models against baselines.

Uses same data splits for fair comparison.
"""

import csv
import json
import numpy as np
from pathlib import Path
from typing import Dict, List
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, brier_score_loss, confusion_matrix,
    balanced_accuracy_score, matthews_corrcoef
)


class BaselineComparator:
    """Compare ML models against baselines."""
    
    def __init__(self):
        self.comparison_results = {}
    
    def load_labeled_data(self, data_dir: Path) -> List[Dict]:
        """Load labeled schedule delay data."""
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
        """Extract numeric features."""
        feature_names = [
            'original_cost_crore', 'revised_cost_crore', 'cumulative_expenditure_crore',
            'physical_progress_pct'
        ]
        
        features = []
        for record in records:
            row = []
            for fname in feature_names:
                val = record.get(fname)
                try:
                    row.append(float(val) if val else 0.0)
                except (ValueError, TypeError):
                    row.append(0.0)
            features.append(row)
        
        return np.array(features)
    
    def extract_target(self, records: List[Dict], target_name: str = 'delay_gt_6_months') -> np.ndarray:
        """Extract target variable."""
        target = []
        for record in records:
            val = record.get(target_name)
            try:
                target.append(int(val) if val is not None else 0)
            except (ValueError, TypeError):
                target.append(0)
        
        return np.array(target)
    
    def evaluate_model(self, y_true: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray) -> Dict:
        """Evaluate model with comprehensive metrics."""
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        return {
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1': f1_score(y_true, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_true, y_proba) if len(set(y_true)) > 1 else 0.5,
            'pr_auc': average_precision_score(y_true, y_proba),
            'brier': brier_score_loss(y_true, y_proba),
            'balanced_accuracy': balanced_accuracy_score(y_true, y_pred),
            'mcc': matthews_corrcoef(y_true, y_pred),
            'confusion_matrix': {
                'true_negative': int(tn),
                'false_positive': int(fp),
                'false_negative': int(fn),
                'true_positive': int(tp)
            }
        }
    
    def majority_class_baseline(self, y_train: np.ndarray, y_test: np.ndarray) -> Dict:
        """Majority class baseline."""
        majority_class = 1 if sum(y_train) > len(y_train) / 2 else 0
        y_pred = np.array([majority_class] * len(y_test))
        y_proba = np.array([float(majority_class)] * len(y_test))
        
        return self.evaluate_model(y_test, y_pred, y_proba)
    
    def logistic_regression_baseline(self, X_train: np.ndarray, y_train: np.ndarray,
                                   X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Logistic Regression baseline."""
        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        return self.evaluate_model(y_test, y_pred, y_proba)
    
    def run_comparison(self, data_dir: Path) -> Dict:
        """Run baseline comparison."""
        print("Running baseline comparison...")
        
        # Load data
        train_records, holdout_records = self.load_labeled_data(data_dir)
        
        # Extract features and targets
        X_train = self.extract_features(train_records)
        y_train = self.extract_target(train_records)
        X_test = self.extract_features(holdout_records)
        y_test = self.extract_target(holdout_records)
        
        print(f"Training samples: {len(X_train)}")
        print(f"Test samples: {len(X_test)}")
        print(f"Target distribution: {sum(y_train)}/{len(y_train)} positive")
        
        # Run baselines
        print("\nRunning majority class baseline...")
        majority_metrics = self.majority_class_baseline(y_train, y_test)
        
        print("Running logistic regression baseline...")
        lr_metrics = self.logistic_regression_baseline(X_train, y_train, X_test, y_test)
        
        # Load ML model metrics
        with open(data_dir / 'results' / 'experimental_model_metrics.json', 'r') as f:
            ml_metrics = json.load(f)
        
        # Compile comparison
        comparison = {
            'majority_class': majority_metrics,
            'logistic_regression': lr_metrics,
            'random_forest': ml_metrics['random_forest'],
            'xgboost': ml_metrics['xgboost'],
            'lightgbm': ml_metrics['lightgbm']
        }
        
        # Save comparison
        output_path = data_dir / 'results' / 'model_comparison.csv'
        lines = [['model', 'precision', 'recall', 'f1', 'roc_auc', 'pr_auc', 'brier', 'balanced_accuracy', 'mcc']]
        
        for model_name, metrics in comparison.items():
            lines.append([
                model_name,
                f"{metrics['precision']:.4f}",
                f"{metrics['recall']:.4f}",
                f"{metrics['f1']:.4f}",
                f"{metrics['roc_auc']:.4f}",
                f"{metrics['pr_auc']:.4f}",
                f"{metrics['brier']:.4f}",
                f"{metrics['balanced_accuracy']:.4f}",
                f"{metrics['mcc']:.4f}"
            ])
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(lines)
        
        print(f"\nComparison saved: {output_path}")
        
        # Print comparison
        print("\nModel Comparison (F1 Score):")
        for model_name, metrics in comparison.items():
            print(f"  {model_name}: {metrics['f1']:.4f}")
        
        return comparison


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    
    comparator = BaselineComparator()
    comparison = comparator.run_comparison(data_dir)
