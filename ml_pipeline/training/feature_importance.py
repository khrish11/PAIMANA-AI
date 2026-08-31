"""Generate feature importance analysis for experimental models."""

import json
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, List


class FeatureImportanceAnalyzer:
    """Analyze feature importance across models."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.feature_names = self.load_feature_names()
    
    def load_feature_names(self) -> List[str]:
        """Load feature names from artifact."""
        with open(self.data_dir / 'artifacts' / 'experimental' / 'feature_names.json', 'r') as f:
            return json.load(f)
    
    def load_model(self, model_name: str):
        """Load model artifact."""
        return joblib.load(self.data_dir / 'artifacts' / 'experimental' / f'{model_name}_experimental.pkl')
    
    def analyze_native_importance(self, model, model_name: str) -> Dict:
        """Analyze native feature importance."""
        try:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
            elif hasattr(model, 'get_booster'):
                importances = model.get_booster().get_score(importance_type='weight')
                # Convert to array in correct order
                importances = np.array([importances.get(f'f{i}', 0) for i in range(len(self.feature_names))])
            else:
                return {}
            
            # Normalize to sum to 1
            importances = importances / np.sum(importances)
            
            feature_importance = {}
            for i, fname in enumerate(self.feature_names):
                feature_importance[fname] = float(importances[i])
            
            return feature_importance
        except Exception as e:
            print(f"Error analyzing native importance for {model_name}: {e}")
            return {}
    
    def compare_feature_stability(self) -> Dict:
        """Compare feature importance stability across models."""
        models = ['random_forest', 'xgboost', 'lightgbm']
        
        all_importances = {}
        for model_name in models:
            model = self.load_model(model_name)
            importance = self.analyze_native_importance(model, model_name)
            all_importances[model_name] = importance
        
        # Calculate stability (standard deviation across models)
        feature_stability = {}
        for fname in self.feature_names:
            values = [all_importances[m].get(fname, 0) for m in models]
            feature_stability[fname] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                'cv': np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
            }
        
        return {
            'all_importances': all_importances,
            'feature_stability': feature_stability
        }
    
    def generate_report(self) -> str:
        """Generate feature importance report."""
        analysis = self.compare_feature_stability()
        
        lines = [
            "# Feature Importance Analysis - Experimental Models",
            "",
            "## Native Feature Importance",
            ""
        ]
        
        # Table of importances
        lines.append("| Feature | Random Forest | XGBoost | LightGBM | Mean | Std | CV |")
        lines.append("|---------|---------------|---------|----------|------|-----|----|")
        
        for fname in self.feature_names:
            rf_imp = analysis['all_importances']['random_forest'].get(fname, 0)
            xgb_imp = analysis['all_importances']['xgboost'].get(fname, 0)
            lgb_imp = analysis['all_importances']['lightgbm'].get(fname, 0)
            stability = analysis['feature_stability'][fname]
            
            lines.append(
                f"| {fname} | {rf_imp:.4f} | {xgb_imp:.4f} | {lgb_imp:.4f} | "
                f"{stability['mean']:.4f} | {stability['std']:.4f} | {stability['cv']:.4f} |"
            )
        
        lines.append("")
        lines.append("## Feature Stability")
        lines.append("")
        lines.append("Lower CV (coefficient of variation) indicates more stable importance across models.")
        lines.append("")
        
        # Sort by stability
        sorted_features = sorted(
            analysis['feature_stability'].items(),
            key=lambda x: x[1]['cv']
        )
        
        for fname, stats in sorted_features:
            lines.append(f"- **{fname}**: CV={stats['cv']:.4f} (mean={stats['mean']:.4f}, std={stats['std']:.4f})")
        
        lines.append("")
        lines.append("## Interpretation")
        lines.append("")
        lines.append("Features with high mean importance and low CV are the most stable predictors.")
        lines.append("Features with high CV indicate model disagreement on feature importance.")
        
        return '\n'.join(lines)


if __name__ == '__main__':
    data_dir = Path(__file__).parent.parent.parent / 'data'
    
    analyzer = FeatureImportanceAnalyzer(data_dir)
    report = analyzer.generate_report()
    
    output_path = data_dir / 'docs' / 'feature_importance_real_data.md'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"Feature importance report saved: {output_path}")
    print("\nTop Features by Mean Importance:")
    
    analysis = analyzer.compare_feature_stability()
    sorted_features = sorted(
        analysis['feature_stability'].items(),
        key=lambda x: x[1]['mean'],
        reverse=True
    )
    
    for fname, stats in sorted_features:
        print(f"  {fname}: {stats['mean']:.4f} (CV={stats['cv']:.4f})")
