# Experimental Model Card - PAIMANA ML

**STATUS: EXPERIMENTAL / DATA-CONSTRAINED**

**IMPORTANT:** These models demonstrate technical feasibility and provide experimental predictions, but the available completed-project labels are insufficient for a production accuracy claim.

---

## Dataset

### Overview
- **Total projects:** 2,705
- **Total observations:** 20,261
- **Temporal coverage:** July 2025 - July 2026 (13 months)
- **Valid labeled projects:** 160 (9.6% of total)
- **Training samples:** 155 (excluding July 2026 holdout)
- **Holdout samples:** 5 (July 2026)

### Data Quality
- Quality gate: 72.7% VALID, 23.8% WARNING, 3.5% EXCLUDE
- Temporal leakage: 20,265/20,265 tests PASSED
- July 2026 holdout: PRESERVED (no training contamination)

---

## Limitations

### Small Sample Size
- Only 160 projects have valid final cost/schedule labels
- 2,545 projects excluded (not completed within 13-month window)
- Insufficient for reliable supervised ML training
- Target: 500+ completed projects for production readiness

### Target Imbalance
- Primary target (delay_gt_6_months): 59.4% positive
- Moderate imbalance requires class weighting
- Some targets have severe imbalance (2.8% - 83.5% positive)

### Short Temporal Window
- 13-month window insufficient for most projects to complete
- Infrastructure projects typically require 2-5 years
- Historical OCMS data needed for longer time horizon

### Extraction/Quality Issues
- 3,805 cost anomalies (835 data quality issues)
- 115 value conflicts from multiple tables
- 3.5% of records excluded by quality gate

---

## Models

### Random Forest (rf-exp-v1)

**Configuration:**
- n_estimators: 100
- max_depth: 10
- class_weight: balanced
- random_state: 42

**Metrics (July 2026 holdout):**
- Precision: 1.0000
- Recall: 0.6667
- F1: 0.8000
- ROC-AUC: 0.8333
- PR-AUC: 0.9444
- Brier: 0.1333
- Balanced Accuracy: 0.8333
- MCC: 0.7303

**Status:** EXPERIMENTAL

---

### XGBoost (xgb-exp-v1)

**Configuration:**
- n_estimators: 100
- max_depth: 6
- learning_rate: 0.1
- scale_pos_weight: 0.67 (class weighting)
- random_state: 42

**Metrics (July 2026 holdout):**
- Precision: 1.0000
- Recall: 1.0000
- F1: 1.0000
- ROC-AUC: 1.0000
- PR-AUC: 1.0000
- Brier: 0.0000
- Balanced Accuracy: 1.0000
- MCC: 1.0000

**Status:** EXPERIMENTAL
**Note:** Perfect metrics on 5-sample holdout likely reflect small sample size, not true performance.

---

### LightGBM (lgb-exp-v1)

**Configuration:**
- n_estimators: 100
- max_depth: 6
- learning_rate: 0.1
- is_unbalance: True
- random_state: 42

**Metrics (July 2026 holdout):**
- Precision: 1.0000
- Recall: 0.6667
- F1: 0.8000
- ROC-AUC: 0.8333
- PR-AUC: 0.9444
- Brier: 0.1333
- Balanced Accuracy: 0.8333
- MCC: 0.7303

**Status:** EXPERIMENTAL

---

## Baseline Comparison

| Model | Precision | Recall | F1 | ROC-AUC | PR-AUC | Brier |
|-------|-----------|--------|----|---------|--------|-------|
| Majority Class | 0.5714 | 1.0000 | 0.5714 | 0.5000 | 0.5944 | 0.4000 |
| Logistic Regression | 0.5714 | 1.0000 | 0.5714 | 0.5000 | 0.5944 | 0.4000 |
| Random Forest | 1.0000 | 0.6667 | 0.8000 | 0.8333 | 0.9444 | 0.1333 |
| XGBoost | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| LightGBM | 1.0000 | 0.6667 | 0.8000 | 0.8333 | 0.9444 | 0.1333 |

**Interpretation:** ML models outperform baselines on F1 score, but perfect XGBoost metrics reflect small holdout size (5 samples).

---

## Feature Importance

### Top Features (Mean Importance)
1. **cumulative_expenditure_crore**: 0.3547 (CV=0.0392)
2. **original_cost_crore**: 0.3533 (CV=0.0313)
3. **revised_cost_crore**: 0.2920 (CV=0.0836)
4. **physical_progress_pct**: 0.0000 (CV=0.0000)

**Stability:** Cost features show stable importance across models (low CV). Progress feature has zero importance, likely because target is delay (time-based) not progress-based.

---

## SHAP Explanations

**Status:** PARTIALLY AVAILABLE
- XGBoost: 5 explanations generated
- LightGBM: 5 explanations generated
- Random Forest: Failed (SHAP compatibility issue)

**Limitations:** SHAP requires C++ build tools not available in current environment. Explanations available for XGBoost and LightGBM only.

---

## Calibration

**Status:** NOT CALIBRATED
- Platt scaling: Not applied
- Isotonic regression: Not applied
- Brier scores: Available but not optimized

**Reasoning:** Calibration requires validation data separate from holdout. With only 160 labeled samples, calibration would consume too much data.

---

## Target Definition

**Primary Target:** `delay_gt_6_months`
- Definition: Project delayed by >6 months (actual_completion_date - original_completion_date > 6)
- Sample: 160 labeled projects
- Positive rate: 59.4% (95/160)
- Type: Binary classification

**Alternative Targets Available:**
- `cost_overrun_5pct`: 9.4% positive (15/160)
- `cost_overrun_10pct`: 9.4% positive (15/160)
- `cost_overrun_20pct`: 7.5% positive (12/160)
- `delay_gt_3_months`: 66.2% positive (106/160)
- `delay_gt_12_months`: 41.9% positive (67/160)
- `future_3m_cost_revision`: 2.8% positive (492/17,556)
- `future_3m_progress_stall`: 83.5% positive (14,659/17,556)

---

## Training/Validation Split

**Training Period:** July 2025 - June 2026 (155 samples)
**Validation Period:** July 2026 (5 samples)
**Holdout:** July 2026 preserved (no training contamination)

**Split Type:** Temporal (chronological)
**Cross-Validation:** Not used (small sample size)

---

## Model Artifacts

**Location:** `data/artifacts/experimental/`
- `random_forest_experimental.pkl`
- `xgboost_experimental.pkl`
- `lightgbm_experimental.pkl`
- `feature_names.json`

**Registry:** `data/artifacts/model_registry.json`
- All models registered with status: `experimental`
- No models marked as `active`

---

## Predictions

**Files Generated:**
- `data/results/random_forest_predictions.csv`
- `data/results/xgboost_predictions.csv`
- `data/results/lightgbm_predictions.csv`

**Fields:**
- project_id
- reporting_month
- predicted_probability
- predicted_class
- actual_label
- model_version

**July 2026 Holdout:** 5 predictions generated (labels not modified)

---

## Use Cases

**Appropriate:**
- Technical feasibility demonstration
- Exploratory analysis
- Feature importance understanding
- Baseline for future models
- Integration into demo with clear experimental labeling

**NOT Appropriate:**
- Production decision-making
- High-stakes project assessment
- Regulatory compliance
- Contractual obligations
- Any use requiring validated accuracy

---

## Recommendations

### For Production Readiness
1. **Collect historical data:** Obtain OCMS historical data for 2-3 year time horizon
2. **Increase completed projects:** Target 500+ completed projects with valid labels
3. **Refine targets:** Develop more granular early-warning targets
4. **Expand features:** Add sector, state, ministry, historical trend features
5. **Temporal CV:** Implement proper time-series cross-validation
6. **Calibration:** Apply Platt/isotonic calibration on validation data
7. **SHAP:** Install C++ build tools for full SHAP support

### For Current Use
1. **Label clearly:** All outputs must be marked "EXPERIMENTAL"
2. **Show limitations:** Display sample size and data constraints
3. **Combine with baselines:** Use statistical baselines and RCF where available
4. **Anomaly detection:** Deploy operational anomaly detection (no labels required)
5. **Monitor performance:** Track predictions vs actuals as projects complete

---

## Version History

- **v1.0** (2026-08-28): Initial experimental models trained on 160 labeled projects
  - Random Forest, XGBoost, LightGBM
  - Target: delay_gt_6_months
  - Status: EXPERIMENTAL

---

## Disclaimer

**These models are EXPERIMENTAL and NOT PRODUCTION-VALIDATED.**

The available completed-project labels (160 projects) are insufficient for a production accuracy claim. These models demonstrate technical feasibility but should not be used for high-stakes decision-making without additional validation data.

**Users must:**
- Clearly label all outputs as experimental
- Display data limitations prominently
- Not claim production-grade accuracy
- Use results for exploratory purposes only
- Combine with other methods (baselines, RCF, anomaly detection)

**The PAIMANA team assumes no liability for decisions made using these experimental models.**
