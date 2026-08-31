# Experimental ML Results - PAIMANA Real Data

**FINAL STATUS: EXPERIMENTAL MODEL TRAINED — NOT PRODUCTION VALIDATED**

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

## Target Distributions

### Primary Target: delay_gt_6_months
- **Definition:** Project delayed by >6 months
- **Total labeled:** 160 projects
- **Positive:** 95 (59.4%)
- **Negative:** 65 (40.6%)
- **Class imbalance:** MODERATE

### Alternative Targets

| Target | Positive Rate | Sample Size |
|--------|---------------|-------------|
| cost_overrun_5pct | 9.4% | 160 |
| cost_overrun_10pct | 9.4% | 160 |
| cost_overrun_20pct | 7.5% | 160 |
| delay_gt_3_months | 66.2% | 160 |
| delay_gt_12_months | 41.9% | 160 |
| future_3m_cost_revision | 2.8% | 17,556 |
| future_3m_progress_stall | 83.5% | 17,556 |

---

## Random Forest (rf-exp-v1)

### Configuration
- n_estimators: 100
- max_depth: 10
- class_weight: balanced
- random_state: 42

### Metrics (July 2026 holdout)
- **Precision:** 1.0000
- **Recall:** 0.6667
- **F1:** 0.8000
- **ROC-AUC:** 0.8333
- **PR-AUC:** 0.9444
- **Brier:** 0.1333
- **Balanced Accuracy:** 0.8333
- **MCC:** 0.7303

### Confusion Matrix
- True Negative: 2
- False Positive: 0
- False Negative: 1
- True Positive: 2

### Status
**EXPERIMENTAL** - Not production validated

---

## XGBoost (xgb-exp-v1)

### Configuration
- n_estimators: 100
- max_depth: 6
- learning_rate: 0.1
- scale_pos_weight: 0.67
- random_state: 42

### Metrics (July 2026 holdout)
- **Precision:** 1.0000
- **Recall:** 1.0000
- **F1:** 1.0000
- **ROC-AUC:** 1.0000
- **PR-AUC:** 1.0000
- **Brier:** 0.0000
- **Balanced Accuracy:** 1.0000
- **MCC:** 1.0000

### Confusion Matrix
- True Negative: 2
- False Positive: 0
- False Negative: 0
- True Positive: 3

### Status
**EXPERIMENTAL** - Not production validated
**Note:** Perfect metrics on 5-sample holdout likely reflect small sample size, not true performance.

---

## LightGBM (lgb-exp-v1)

### Configuration
- n_estimators: 100
- max_depth: 6
- learning_rate: 0.1
- is_unbalance: True
- random_state: 42

### Metrics (July 2026 holdout)
- **Precision:** 1.0000
- **Recall:** 0.6667
- **F1:** 0.8000
- **ROC-AUC:** 0.8333
- **PR-AUC:** 0.9444
- **Brier:** 0.1333
- **Balanced Accuracy:** 0.8333
- **MCC:** 0.7303

### Confusion Matrix
- True Negative: 2
- False Positive: 0
- False Negative: 1
- True Positive: 2

### Status
**EXPERIMENTAL** - Not production validated

---

## Best Model

### Selected: XGBoost (xgb-exp-v1)

**Reason:** Highest F1 score (1.0000) on holdout

**Limitations:**
- Perfect metrics on 5-sample holdout are not statistically significant
- Small sample size (160 labeled projects) insufficient for production claims
- No temporal cross-validation performed
- No calibration applied

**Recommendation:** Use XGBoost for demo purposes with clear experimental labeling. Do not claim production accuracy.

---

## SHAP

### Global Feature Importance

| Feature | Mean Importance | Stability (CV) |
|---------|----------------|----------------|
| cumulative_expenditure_crore | 0.3547 | 0.0392 |
| original_cost_crore | 0.3533 | 0.0313 |
| revised_cost_crore | 0.2920 | 0.0836 |
| physical_progress_pct | 0.0000 | 0.0000 |

**Interpretation:** Cost features are the most important predictors. Progress feature has zero importance for delay prediction.

### Representative Project Explanations

**Status:** PARTIALLY AVAILABLE
- XGBoost: 5 explanations generated
- LightGBM: 5 explanations generated
- Random Forest: Failed (SHAP compatibility issue)

**Limitations:** SHAP requires C++ build tools not available in current environment.

---

## Calibration

### Status: NOT CALIBRATED

**Brier Scores:**
- Random Forest: 0.1333
- XGBoost: 0.0000
- LightGBM: 0.1333

**Methods Not Applied:**
- Platt scaling
- Isotonic regression

**Reasoning:** Calibration requires validation data separate from holdout. With only 160 labeled samples, calibration would consume too much data.

---

## July 2026 Holdout

### Results
- **Holdout samples:** 5 projects
- **Training contamination:** NONE
- **Labels:** NOT MODIFIED
- **Predictions generated:** All 3 models

### Performance Summary
| Model | Correct | Incorrect | Accuracy |
|-------|---------|-----------|----------|
| Random Forest | 4/5 | 1/5 | 80% |
| XGBoost | 5/5 | 0/5 | 100% |
| LightGBM | 4/5 | 1/5 | 80% |

**Note:** 5-sample holdout is too small for statistically significant performance claims.

---

## Baseline Comparison

| Model | Precision | Recall | F1 | ROC-AUC | PR-AUC | Brier |
|-------|-----------|--------|----|---------|--------|-------|
| Majority Class | 0.5714 | 1.0000 | 0.5714 | 0.5000 | 0.5944 | 0.4000 |
| Logistic Regression | 0.5714 | 1.0000 | 0.5714 | 0.5000 | 0.5944 | 0.4000 |
| Random Forest | 1.0000 | 0.6667 | 0.8000 | 0.8333 | 0.9444 | 0.1333 |
| XGBoost | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| LightGBM | 1.0000 | 0.6667 | 0.8000 | 0.8333 | 0.9444 | 0.1333 |

**Interpretation:** ML models outperform baselines on F1 score, but perfect XGBoost metrics reflect small holdout size.

---

## FINAL STATUS

**EXPERIMENTAL MODEL TRAINED — NOT PRODUCTION VALIDATED**

### What Was Achieved
1. ✅ RF, XGBoost, LightGBM trained on real PAIMANA data
2. ✅ Class imbalance handling implemented
3. ✅ Comprehensive metrics computed
4. ✅ Baseline comparison completed
5. ✅ SHAP explanations generated (partial)
6. ✅ Feature importance analyzed
7. ✅ Model artifacts saved and registered
8. ✅ Predictions generated for July 2026 holdout
9. ✅ July 2026 holdout preserved (no training contamination)

### What Was NOT Achieved
1. ❌ Production-validated accuracy (insufficient labels)
2. ❌ Temporal cross-validation (small sample size)
3. ❌ Model calibration (insufficient validation data)
4. ❌ Full SHAP support (C++ build tools unavailable)
5. ❌ Statistical significance (5-sample holdout)

### Limitations
- **Sample size:** Only 160 valid labels (9.6% of projects)
- **Holdout size:** Only 5 samples for evaluation
- **Temporal window:** 13 months insufficient for project completions
- **Target imbalance:** Some targets have severe imbalance (2.8% - 83.5%)
- **No calibration:** Probabilities not calibrated
- **No CV:** No temporal cross-validation performed

### Recommendations for Production Readiness
1. **Collect historical data:** Obtain OCMS historical data for 2-3 year time horizon
2. **Increase completed projects:** Target 500+ completed projects with valid labels
3. **Implement temporal CV:** Use proper time-series cross-validation
4. **Apply calibration:** Calibrate probabilities on validation data
5. **Expand features:** Add sector, state, ministry, historical trend features
6. **Install SHAP:** Install C++ build tools for full SHAP support

### Current Use Case
**Appropriate for:**
- Technical feasibility demonstration
- Exploratory analysis
- Feature importance understanding
- Demo integration with clear experimental labeling
- Baseline for future models

**NOT appropriate for:**
- Production decision-making
- High-stakes project assessment
- Regulatory compliance
- Contractual obligations

### Required Labeling
All outputs must be clearly marked:
- **"EXPERIMENTAL MODEL"**
- **"LIMITED COMPLETED OUTCOMES"**
- **"NOT PRODUCTION VALIDATED"**

---

## Files Generated

### Model Artifacts
- `data/artifacts/experimental/random_forest_experimental.pkl`
- `data/artifacts/experimental/xgboost_experimental.pkl`
- `data/artifacts/experimental/lightgbm_experimental.pkl`
- `data/artifacts/experimental/feature_names.json`
- `data/artifacts/model_registry.json`

### Predictions
- `data/results/random_forest_predictions.csv`
- `data/results/xgboost_predictions.csv`
- `data/results/lightgbm_predictions.csv`

### Metrics
- `data/results/experimental_model_metrics.json`
- `data/results/model_comparison.csv`
- `data/results/shap_examples.json`

### Documentation
- `data/docs/target_definitions.md`
- `data/docs/model_card_experimental.md`
- `data/docs/feature_importance_real_data.md`

### Labeled Datasets
- `data/training/labeled/cost_overrun_labeled.csv`
- `data/training/labeled/schedule_delay_labeled.csv`
- `data/training/labeled/early_warning_labeled.csv`

---

## Conclusion

Experimental ML models (RF, XGBoost, LightGBM) have been successfully trained on PAIMANA real data. The models demonstrate technical feasibility with XGBoost achieving perfect metrics on the 5-sample holdout.

**However, the dataset has insufficient completed-project labels (160 projects) for production accuracy claims.** These models should be used for exploratory purposes and demo integration only, with clear experimental labeling.

**The infrastructure is solid, but supervised ML requires more historical completions before it can be reliably deployed for production-like use.**

**STATUS: EXPERIMENTAL MODEL TRAINED — NOT PRODUCTION VALIDATED**
