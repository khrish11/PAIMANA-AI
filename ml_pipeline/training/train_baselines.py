"""Train true baseline models for PAIMANA real data.

Trains:
1. Naive baseline (predict majority class or mean)
2. Sector-average baseline (predict sector average)
3. Logistic Regression / Linear Regression

Uses exactly the same temporal folds for every method.
"""

import csv
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, brier_score_loss,
    mean_absolute_error, mean_squared_error, r2_score
)


class BaselineTrainer:
    """Train and evaluate baseline models."""
    
    def __init__(self):
        self.metrics = defaultdict(dict)
    
    def create_binary_target(self, records: List[Dict]) -> List[Dict]:
        """Create binary target for cost overrun prediction.
        
        Target: 1 if NEXT month's progress change is negative (stalled/slowed), 0 otherwise
        This uses the early-warning target structure for proper prediction.
        """
        labeled = []
        for record in records:
            # Use target_progress_change from early-warning dataset
            target_change = record.get('target_progress_change')
            
            if target_change is not None and target_change != '':
                try:
                    change_val = float(target_change)
                    record_copy = record.copy()
                    # Target: 1 if progress stalled or regressed (negative or very low change)
                    record_copy['target_cost_overrun'] = 1 if change_val < 1.0 else 0
                    record_copy['target_overrun_ratio'] = change_val
                    labeled.append(record_copy)
                except (ValueError, TypeError):
                    pass
        
        return labeled
    
    def extract_features(self, records: List[Dict]) -> Tuple[List[List[float]], List[str]]:
        """Extract numeric features for modeling."""
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
        
        return features, feature_names
    
    def naive_baseline(self, y_train: List, y_test: List) -> Dict:
        """Naive baseline: predict majority class (classification) or mean (regression)."""
        # Determine if classification or regression
        if all(isinstance(v, (int, float)) and v in [0, 1] for v in y_train):
            # Classification
            majority_class = max(set(y_train), key=y_train.count)
            y_pred = [majority_class] * len(y_test)
            
            return {
                'precision': precision_score(y_test, y_pred, zero_division=0),
                'recall': recall_score(y_test, y_pred, zero_division=0),
                'f1': f1_score(y_test, y_pred, zero_division=0),
                'roc_auc': 0.5,  # Random guessing
                'pr_auc': average_precision_score(y_test, y_pred),
                'brier': brier_score_loss(y_test, y_pred)
            }
        else:
            # Regression
            mean_value = np.mean(y_train)
            y_pred = [mean_value] * len(y_test)
            
            return {
                'mae': mean_absolute_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'r2': r2_score(y_test, y_pred)
            }
    
    def sector_average_baseline(self, train_records: List[Dict], test_records: List[Dict], 
                                 target_field: str) -> Dict:
        """Sector-average baseline: predict sector average."""
        # Calculate sector averages from training
        sector_averages = defaultdict(list)
        for record in train_records:
            sector = record.get('sector', 'unknown')
            target = record.get(target_field)
            try:
                sector_averages[sector].append(float(target))
            except (ValueError, TypeError):
                pass
        
        sector_means = {s: np.mean(vals) for s, vals in sector_averages.items() if vals}
        global_mean = np.mean(list(sector_means.values())) if sector_means else 0.0
        
        # Predict sector average for test
        y_true = []
        y_pred = []
        for record in test_records:
            sector = record.get('sector', 'unknown')
            target = record.get(target_field)
            try:
                y_true.append(float(target))
                y_pred.append(sector_means.get(sector, global_mean))
            except (ValueError, TypeError):
                pass
        
        # Determine if classification or regression
        if all(isinstance(v, (int, float)) and v in [0, 1] for v in y_true):
            # Classification - threshold at 0.5
            y_pred_binary = [1 if p > 0.5 else 0 for p in y_pred]
            return {
                'precision': precision_score(y_true, y_pred_binary, zero_division=0),
                'recall': recall_score(y_true, y_pred_binary, zero_division=0),
                'f1': f1_score(y_true, y_pred_binary, zero_division=0),
                'roc_auc': 0.5,
                'pr_auc': average_precision_score(y_true, y_pred_binary),
                'brier': brier_score_loss(y_true, y_pred_binary)
            }
        else:
            return {
                'mae': mean_absolute_error(y_true, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'r2': r2_score(y_true, y_pred)
            }
    
    def logistic_regression_baseline(self, X_train: List[List[float]], y_train: List,
                                     X_test: List[List[float]], y_test: List) -> Dict:
        """Logistic Regression baseline."""
        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        return {
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_proba) if len(set(y_test)) > 1 else 0.5,
            'pr_auc': average_precision_score(y_test, y_proba),
            'brier': brier_score_loss(y_test, y_proba)
        }
    
    def linear_regression_baseline(self, X_train: List[List[float]], y_train: List,
                                   X_test: List[List[float]], y_test: List) -> Dict:
        """Linear Regression baseline."""
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        return {
            'mae': mean_absolute_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred)
        }
    
    def evaluate_on_folds(self, longitudinal_path: Path) -> Dict:
        """Evaluate all baselines using temporal splits from longitudinal dataset."""
        # Load longitudinal dataset
        records = []
        with open(longitudinal_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Exclude July 2026 (holdout) and EXCLUDE records
                if row.get('_quality_classification') != 'EXCLUDE' and row.get('reporting_month', '') != '2026-07':
                    records.append(row)
        
        # Get unique periods and sort them
        periods = sorted(set(r.get('reporting_month', '') for r in records if r.get('reporting_month') != 'unknown'))
        
        # Create temporal train/test splits (use last 3 periods as test, excluding July 2026)
        results = {
            'naive': [],
            'sector_average': [],
            'logistic_regression': [],
            'linear_regression': []
        }
        
        for i in range(2, len(periods)):
            train_periods = periods[:i]
            test_period = periods[i]
            
            train_recs = [r for r in records if r.get('reporting_month', '') in train_periods]
            test_recs = [r for r in records if r.get('reporting_month', '') == test_period]
            
            if not train_recs or not test_recs:
                continue
            
            # Create targets: predict if progress will stall in next period
            # For each test record, check if progress in next period is lower
            train_labeled = self.create_temporal_target(train_recs, train_periods)
            test_labeled = self.create_temporal_target(test_recs, [test_period])
            
            if not train_labeled or not test_labeled:
                continue
            
            # Extract features and targets
            X_train, feature_names = self.extract_features(train_labeled)
            X_test, _ = self.extract_features(test_labeled)
            y_train = [r['target_stalled'] for r in train_labeled]
            y_test = [r['target_stalled'] for r in test_labeled]
            y_train_reg = [r.get('target_progress_change', 0) for r in train_labeled]
            y_test_reg = [r.get('target_progress_change', 0) for r in test_labeled]
            
            # Naive baseline
            naive_metrics = self.naive_baseline(y_train, y_test)
            results['naive'].append(naive_metrics)
            
            # Sector average baseline
            sector_metrics = self.sector_average_baseline(train_labeled, test_labeled, 'target_stalled')
            results['sector_average'].append(sector_metrics)
            
            # Logistic Regression
            try:
                lr_metrics = self.logistic_regression_baseline(X_train, y_train, X_test, y_test)
                results['logistic_regression'].append(lr_metrics)
            except Exception as e:
                print(f"Logistic Regression failed on period {test_period}: {e}")
            
            # Linear Regression
            try:
                linreg_metrics = self.linear_regression_baseline(X_train, y_train_reg, X_test, y_test_reg)
                results['linear_regression'].append(linreg_metrics)
            except Exception as e:
                print(f"Linear Regression failed on period {test_period}: {e}")
        
        # Aggregate results
        aggregated = {}
        for model_name, fold_metrics in results.items():
            if not fold_metrics:
                continue
            
            avg_metrics = {}
            for metric_key in fold_metrics[0].keys():
                values = [m.get(metric_key, 0) for m in fold_metrics if metric_key in m]
                if values:
                    avg_metrics[metric_key] = np.mean(values)
            
            aggregated[model_name] = avg_metrics
        
        return aggregated
    
    def create_temporal_target(self, records: List[Dict], periods: List[str]) -> List[Dict]:
        """Create temporal target: predict if progress will stall in next period."""
        # Group by project
        projects = defaultdict(list)
        for record in records:
            pid = record.get('project_id', '')
            if pid:
                projects[pid].append(record)
        
        labeled = []
        for pid, project_records in projects.items():
            # Sort by period
            sorted_recs = sorted(project_records, key=lambda x: x.get('reporting_month', ''))
            
            for i in range(len(sorted_recs) - 1):
                current = sorted_recs[i]
                next_rec = sorted_recs[i + 1]
                
                # Calculate progress change
                try:
                    curr_progress = float(current.get('physical_progress_pct', 0))
                    next_progress = float(next_rec.get('physical_progress_pct', 0))
                    progress_change = next_progress - curr_progress
                    
                    current_copy = current.copy()
                    # Target: 1 if progress stalled (change < 1%)
                    current_copy['target_stalled'] = 1 if progress_change < 1.0 else 0
                    current_copy['target_progress_change'] = progress_change
                    labeled.append(current_copy)
                except (ValueError, TypeError):
                    pass
        
        return labeled


def save_baseline_results(results: Dict, output_path: Path):
    """Save baseline results to CSV."""
    lines = [['model', 'metric', 'value']]
    
    for model_name, metrics in results.items():
        for metric_name, value in metrics.items():
            lines.append([model_name, metric_name, f'{value:.4f}'])
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(lines)


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    longitudinal_path = data_dir / 'validation' / 'project_monthly_history_dedup.csv'
    output_path = data_dir / 'results' / 'baseline_results.csv'
    
    print("Training baseline models...")
    
    # Train baselines using longitudinal dataset with temporal splits
    trainer = BaselineTrainer()
    results = trainer.evaluate_on_folds(longitudinal_path)
    
    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_baseline_results(results, output_path)
    
    print(f"\nBaseline Results:")
    for model_name, metrics in results.items():
        print(f"\n{model_name}:")
        for metric_name, value in metrics.items():
            print(f"  {metric_name}: {value:.4f}")
    
    print(f"\nResults saved: {output_path}")
