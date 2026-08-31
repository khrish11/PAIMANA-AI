# Feature Importance Analysis - Experimental Models

## Native Feature Importance

| Feature | Random Forest | XGBoost | LightGBM | Mean | Std | CV |
|---------|---------------|---------|----------|------|-----|----|
| original_cost_crore | 0.3387 | 0.3556 | 0.3655 | 0.3533 | 0.0111 | 0.0313 |
| revised_cost_crore | 0.3262 | 0.2789 | 0.2708 | 0.2920 | 0.0244 | 0.0836 |
| cumulative_expenditure_crore | 0.3351 | 0.3655 | 0.3636 | 0.3547 | 0.0139 | 0.0392 |
| physical_progress_pct | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## Feature Stability

Lower CV (coefficient of variation) indicates more stable importance across models.

- **physical_progress_pct**: CV=0.0000 (mean=0.0000, std=0.0000)
- **original_cost_crore**: CV=0.0313 (mean=0.3533, std=0.0111)
- **cumulative_expenditure_crore**: CV=0.0392 (mean=0.3547, std=0.0139)
- **revised_cost_crore**: CV=0.0836 (mean=0.2920, std=0.0244)

## Interpretation

Features with high mean importance and low CV are the most stable predictors.
Features with high CV indicate model disagreement on feature importance.