"""Build training datasets with temporal leakage protection."""

import csv
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime


def sort_periods(periods: List[str]) -> List[str]:
    """Sort reporting periods chronologically."""
    def period_key(p: str) -> Tuple[int, int]:
        if '-' in p and len(p) >= 7:
            year, month = p.split('-')[:2]
            try:
                return (int(year), int(month))
            except ValueError:
                return (9999, 12)
        return (9999, 12)
    
    return sorted(periods, key=period_key)


def build_as_of_date_features(record: Dict, historical_records: List[Dict]) -> Dict:
    """Build as-of-date features using only historical data."""
    features = record.copy()
    
    # Only use records from earlier periods
    current_period = record.get('reporting_month', '')
    historical = [r for r in historical_records 
                  if r.get('reporting_month', '') < current_period 
                  and r.get('project_id') == record.get('project_id')]
    
    if not historical:
        features['historical_obs_count'] = 0
        features['avg_progress_historical'] = None
        features['progress_trend'] = None
        features['cost_increase_rate'] = None
        return features
    
    # Sort historical by period
    historical = sorted(historical, key=lambda x: x.get('reporting_month', ''))
    
    features['historical_obs_count'] = len(historical)
    
    # Calculate historical progress trend
    progress_values = []
    for h in historical:
        try:
            prog = float(h.get('physical_progress_pct', 0)) if h.get('physical_progress_pct') else None
            if prog is not None:
                progress_values.append(prog)
        except (ValueError, TypeError):
            pass
    
    if progress_values:
        features['avg_progress_historical'] = sum(progress_values) / len(progress_values)
        if len(progress_values) >= 2:
            features['progress_trend'] = progress_values[-1] - progress_values[0]
        else:
            features['progress_trend'] = 0
    else:
        features['avg_progress_historical'] = None
        features['progress_trend'] = None
    
    # Calculate cost increase rate
    cost_values = []
    for h in historical:
        try:
            cost = float(h.get('revised_cost_crore', 0)) if h.get('revised_cost_crore') else None
            if cost is not None:
                cost_values.append(cost)
        except (ValueError, TypeError):
            pass
    
    if cost_values:
        features['cost_increase_rate'] = (cost_values[-1] - cost_values[0]) / cost_values[0] if cost_values[0] > 0 else 0
    else:
        features['cost_increase_rate'] = None
    
    return features


def create_train_test_split(records: List[Dict], test_period: str) -> Tuple[List[Dict], List[Dict]]:
    """Create temporal train/test split with leakage protection.
    
    All records from periods before test_period go to train.
    Records from test_period go to test.
    """
    train = [r for r in records if r.get('reporting_month', '') < test_period]
    test = [r for r in records if r.get('reporting_month', '') == test_period]
    
    return train, test


def create_time_series_folds(records: List[Dict], min_periods: int = 2) -> List[Tuple[List[Dict], List[Dict]]]:
    """Create time-series cross-validation folds.
    
    Each fold uses earlier periods for training, later period for validation.
    """
    periods = sort_periods(list(set(r.get('reporting_month', '') for r in records if r.get('reporting_month') != 'unknown')))
    
    folds = []
    for i in range(min_periods, len(periods)):
        train_periods = periods[:i]
        test_period = periods[i]
        
        train = [r for r in records if r.get('reporting_month', '') in train_periods]
        test = [r for r in records if r.get('reporting_month', '') == test_period]
        
        if train and test:
            folds.append((train, test))
    
    return folds


def build_early_warning_dataset(records: List[Dict]) -> List[Dict]:
    """Build dataset for early warning prediction.
    
    Target: Future progress or cost overrun indicators.
    Features: Current project state with historical context.
    """
    periods = sort_periods(list(set(r.get('reporting_month', '') for r in records if r.get('reporting_month') != 'unknown')))
    
    early_warning_records = []
    
    # For each period (except last), predict next period's outcome
    for i in range(len(periods) - 1):
        current_period = periods[i]
        next_period = periods[i + 1]
        
        current_records = [r for r in records if r.get('reporting_month', '') == current_period]
        next_records = [r for r in records if r.get('reporting_month', '') == next_period]
        
        # Build lookup for next period values
        next_lookup = {r.get('project_id'): r for r in next_records}
        
        for record in current_records:
            pid = record.get('project_id', '')
            next_record = next_lookup.get(pid)
            
            # Build features with historical context
            features = build_as_of_date_features(record, records)
            
            # Add target variables from next period
            if next_record:
                try:
                    features['target_next_progress'] = float(next_record.get('physical_progress_pct', 0)) if next_record.get('physical_progress_pct') else None
                except (ValueError, TypeError):
                    features['target_next_progress'] = None
                
                try:
                    features['target_next_expenditure'] = float(next_record.get('cumulative_expenditure_crore', 0)) if next_record.get('cumulative_expenditure_crore') else None
                except (ValueError, TypeError):
                    features['target_next_expenditure'] = None
                
                # Calculate progress change
                try:
                    curr_prog = float(record.get('physical_progress_pct', 0)) if record.get('physical_progress_pct') else 0
                    next_prog = float(next_record.get('physical_progress_pct', 0)) if next_record.get('physical_progress_pct') else 0
                    features['target_progress_change'] = next_prog - curr_prog
                except (ValueError, TypeError):
                    features['target_progress_change'] = None
            else:
                features['target_next_progress'] = None
                features['target_next_expenditure'] = None
                features['target_progress_change'] = None
            
            early_warning_records.append(features)
    
    return early_warning_records


def build_anomaly_detection_dataset(records: List[Dict]) -> List[Dict]:
    """Build dataset for anomaly detection.
    
    Features: Project metrics relative to sector/state benchmarks.
    """
    # Calculate sector benchmarks
    sector_stats = defaultdict(lambda: {'cost': [], 'progress': [], 'expenditure': []})
    
    for record in records:
        sector = record.get('sector', 'unknown')
        try:
            cost = float(record.get('revised_cost_crore', 0)) if record.get('revised_cost_crore') else None
            if cost:
                sector_stats[sector]['cost'].append(cost)
        except (ValueError, TypeError):
            pass
        
        try:
            progress = float(record.get('physical_progress_pct', 0)) if record.get('physical_progress_pct') else None
            if progress is not None:
                sector_stats[sector]['progress'].append(progress)
        except (ValueError, TypeError):
            pass
        
        try:
            expenditure = float(record.get('cumulative_expenditure_crore', 0)) if record.get('cumulative_expenditure_crore') else None
            if expenditure:
                sector_stats[sector]['expenditure'].append(expenditure)
        except (ValueError, TypeError):
            pass
    
    # Calculate sector means
    sector_means = {}
    for sector, stats in sector_stats.items():
        sector_means[sector] = {
            'cost_mean': sum(stats['cost']) / len(stats['cost']) if stats['cost'] else None,
            'progress_mean': sum(stats['progress']) / len(stats['progress']) if stats['progress'] else None,
            'expenditure_mean': sum(stats['expenditure']) / len(stats['expenditure']) if stats['expenditure'] else None
        }
    
    # Add deviation features
    anomaly_records = []
    for record in records:
        features = record.copy()
        sector = record.get('sector', 'unknown')
        means = sector_means.get(sector, {})
        
        try:
            cost = float(record.get('revised_cost_crore', 0)) if record.get('revised_cost_crore') else None
            if cost and means.get('cost_mean'):
                features['cost_deviation_from_sector'] = (cost - means['cost_mean']) / means['cost_mean']
            else:
                features['cost_deviation_from_sector'] = None
        except (ValueError, TypeError):
            features['cost_deviation_from_sector'] = None
        
        try:
            progress = float(record.get('physical_progress_pct', 0)) if record.get('physical_progress_pct') else None
            if progress is not None and means.get('progress_mean'):
                features['progress_deviation_from_sector'] = progress - means['progress_mean']
            else:
                features['progress_deviation_from_sector'] = None
        except (ValueError, TypeError):
            features['progress_deviation_from_sector'] = None
        
        anomaly_records.append(features)
    
    return anomaly_records


def save_dataset(records: List[Dict], output_path: Path):
    """Save dataset to CSV."""
    if not records:
        return
    
    fieldnames = list(records[0].keys())
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def build_all_training_datasets(input_path: Path, output_dir: Path) -> Dict:
    """Build all training datasets with temporal leakage protection."""
    # Read records
    records = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build early warning dataset
    print("Building early warning dataset...")
    early_warning = build_early_warning_dataset(records)
    ew_path = output_dir / 'early_warning_dataset.csv'
    save_dataset(early_warning, ew_path)
    
    # Build anomaly detection dataset
    print("Building anomaly detection dataset...")
    anomaly = build_anomaly_detection_dataset(records)
    anomaly_path = output_dir / 'anomaly_detection_dataset.csv'
    save_dataset(anomaly, anomaly_path)
    
    # Create time-series CV folds
    print("Creating time-series cross-validation folds...")
    folds = create_time_series_folds(records)
    folds_dir = output_dir / 'time_series_folds'
    folds_dir.mkdir(exist_ok=True)
    
    for i, (train, test) in enumerate(folds):
        train_path = folds_dir / f'fold_{i}_train.csv'
        test_path = folds_dir / f'fold_{i}_test.csv'
        save_dataset(train, train_path)
        save_dataset(test, test_path)
    
    # Create final train/test split (last period as test)
    periods = sort_periods(list(set(r.get('reporting_month', '') for r in records if r.get('reporting_month') != 'unknown')))
    if periods:
        test_period = periods[-1]
        train, test = create_train_test_split(records, test_period)
        
        train_path = output_dir / 'train_final.csv'
        test_path = output_dir / 'test_final.csv'
        save_dataset(train, train_path)
        save_dataset(test, test_path)
    
    return {
        'early_warning_records': len(early_warning),
        'anomaly_records': len(anomaly),
        'cv_folds': len(folds),
        'train_records': len(train) if periods else 0,
        'test_records': len(test) if periods else 0,
        'test_period': test_period if periods else 'N/A'
    }


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    input_path = data_dir / 'validation' / 'project_monthly_history_dedup.csv'
    output_dir = data_dir / 'training'
    
    print("Building training datasets with temporal leakage protection...")
    results = build_all_training_datasets(input_path, output_dir)
    
    print(f"\nTraining Datasets Created:")
    print(f"  Early warning dataset: {results['early_warning_records']} records")
    print(f"  Anomaly detection dataset: {results['anomaly_records']} records")
    print(f"  Time-series CV folds: {results['cv_folds']}")
    print(f"  Final train set: {results['train_records']} records")
    print(f"  Final test set: {results['test_records']} records")
    print(f"  Test period: {results['test_period']}")
    print(f"\nOutput directory: {output_dir}")
