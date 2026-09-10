# ML Pipeline Audit Report

**Date**: September 1, 2026  
**Purpose**: Audit existing ML models and infrastructure for integration into PAIMANA risk engine

---

## 1. TRAINED MODELS DISCOVERED

### Location
- Model artifacts: `data/artifacts/experimental/v2/`
- Model registry: `data/artifacts/model_registry.json`

### Selected Models for Production

#### Cost Overrun Model: XGBoost v2
- **Model ID**: xgboost_cost_v2
- **Algorithm**: XGBoost
- **Target**: cost_overrun_10pct (binary: final_cost > sanctioned_cost * 1.10)
- **Status**: EXPERIMENTAL_SELECTED
- **Artifact**: data/artifacts/experimental/v2/xgboost_cost_v2.pkl
- **Feature File**: data/artifacts/experimental/v2/cost_feature_names_v2.json
- **Training Date**: 2026-08-31
- **Training Samples**: 274
- **Validation Samples**: 90
- **Test Samples**: 90
- **Target Prevalence**: 50.4%

**Metrics**:
- Test ROC-AUC: 0.809
- Test F1: 0.723
- Test PR-AUC: 0.747
- Test Brier: 0.187
- Test MCC: 0.487
- Validation F1: 0.645
- Validation ROC-AUC: 0.728

**SHAP Status**: Working

**Notes**: Best cost model (Test ROC-AUC: 0.809)

---

#### Schedule Delay Model: LightGBM v2
- **Model ID**: lightgbm_schedule_v2
- **Algorithm**: LightGBM
- **Target**: delay_gt_6_months (binary: revised_date - original_date > 6 months)
- **Status**: EXPERIMENTAL_SELECTED
- **Artifact**: data/artifacts/experimental/v2/lightgbm_schedule_v2.pkl
- **Feature File**: data/artifacts/experimental/v2/schedule_feature_names_v2.json
- **Training Date**: 2026-08-31
- **Training Samples**: 252
- **Validation Samples**: 85
- **Test Samples**: 85
- **Target Prevalence**: 71%

**Metrics**:
- Test ROC-AUC: 0.757
- Test F1: 0.857
- Test PR-AUC: 0.854
- Test Brier: 0.208
- Test MCC: 0.406
- Validation F1: 0.806
- Validation ROC-AUC: 0.695

**SHAP Status**: Working

**Notes**: Best schedule model (Test ROC-AUC: 0.757), trained with stratified split

---

## 2. FEATURE DEFINITIONS

### Cost Model Features (30 features)

**Numerical Features**:
1. completion_by_expenditure: expenditure / sanctioned_cost
2. completion_by_progress: physical_progress / 100
3. cost_revision_ratio: revised_cost / sanctioned_cost
4. log_sanctioned_cost: log(sanctioned_cost)

**Sector One-Hot Encoding** (10 sectors):
5. sector_Aviation & Aviation Infrastructure
6. sector_Electricity Generation
7. sector_Healthcare
8. sector_Oil & Gas
9. sector_PAN India
10. sector_Railways
11. sector_Roads & Highways
12. sector_Shipping
13. sector_Transmission & Distribution
14. sector_Water Resources
15. (Reference: "Unknown" sector is baseline, all zeros)

**Size Band One-Hot Encoding** (5 bands):
16. size_band_LARGE
17. size_band_MEDIUM
18. size_band_SMALL
19. size_band_UNKNOWN
20. size_band_XLARGE
21. (Reference: One band is baseline, all zeros)

**State One-Hot Encoding** (10 states):
22. state_Andhra Pradesh
23. state_Assam
24. state_Bihar
25. state_Gujarat
26. state_Maharashtra
27. state_Odisha
28. state_Rajasthan
29. state_Tamil Nadu
30. state_Uttar Pradesh
31. state_Uttarakhand
32. (Reference: Other states are baseline, all zeros)

---

### Schedule Model Features (28 features)

**Numerical Features**:
1. completion_by_expenditure: expenditure / sanctioned_cost
2. completion_by_progress: physical_progress / 100
3. log_sanctioned_cost: log(sanctioned_cost)

**Sector One-Hot Encoding** (11 sectors):
4. sector_Education
5. sector_Electricity Generation
6. sector_Healthcare
7. sector_Oil & Gas
8. sector_Railways
9. sector_Roads & Highways
10. sector_Transmission & Distribution
11. sector_Urban Public Transport
12. sector_Waste & Water
13. sector_Water Resources
14. (Reference: Other sectors are baseline, all zeros)

**Size Band One-Hot Encoding** (5 bands):
15. size_band_LARGE
16. size_band_MEDIUM
17. size_band_SMALL
18. size_band_UNKNOWN
19. size_band_XLARGE
20. (Reference: One band is baseline, all zeros)

**State One-Hot Encoding** (10 states):
21. state_Andhra Pradesh
22. state_Assam
23. state_Bihar
24. state_Chhattisgarh
25. state_Gujarat
26. state_Karnataka
27. state_Madhya Pradesh
28. state_Maharashtra
29. state_Odisha
30. state_Uttar Pradesh
31. (Reference: Other states are baseline, all zeros)

---

## 3. FEATURE ENGINEERING LOGIC

### From ml_pipeline/data_prep/features.py:

**Required Project Fields**:
- project_id
- sector
- state
- sanctioned_cost
- approved_date

**Required Submission Fields**:
- project_id
- reporting_month
- revised_cost
- expenditure
- physical_progress
- planned_completion
- submitted_at

**Derived Features**:
```python
size_band = size_band_for_cost(sanctioned_cost)
# Bands: 150-500Cr (SMALL), 500-2000Cr (MEDIUM), 2000+Cr (LARGE)

cost_overrun_ratio = revised_cost / sanctioned_cost

completion_by_expenditure = expenditure / sanctioned_cost

completion_by_progress = physical_progress / 100

log_sanctioned_cost = log(sanctioned_cost)

schedule_slip_months = months_between(baseline_planned_completion, planned_completion)

expenditure_to_progress_gap = (expenditure / revised_cost) - (physical_progress / 100)

progress_velocity_3m = (physical_progress - progress_3m_ago) / 3

cost_revision_count = nunique(revised_cost) across submissions

reporting_lag_days = days(submitted_at - reporting_month)
```

**One-Hot Encoding**:
- Sector: One-hot encoded with "Unknown" as baseline
- Size Band: One-hot encoded with one band as baseline
- State: One-hot encoded with "Other" as baseline

---

## 4. CURRENT INFRASTRUCTURE

### Existing ML Inference Service (backend/app/services/ml_inference.py)

**Status**: Incomplete for production use

**Current Features**:
- Loads models via model_loader
- Extracts only 4 features: original_cost_crore, revised_cost_crore, cumulative_expenditure_crore, physical_progress_pct
- No one-hot encoding for sector, size_band, state
- No feature engineering (completion ratios, log transforms)
- No SHAP integration in inference

**Gaps**:
- Missing 26 features for cost model
- Missing 25 features for schedule model
- No one-hot encoding logic
- No feature engineering logic
- No SHAP explainability in inference
- Uses wrong feature names (training uses different names)

---

### Existing Risk Scoring Service (backend/app/services/risk_scoring.py)

**Status**: Rule-based, prepared for ML integration

**Current Logic**:
- Rule-based cost_risk: cost_overrun_ratio * 3.3
- Rule-based schedule_risk: (schedule_slip / planned_duration) * 200
- Rule-based progress_anomaly: anomaly_count * 15 + severity_bonus
- Rule-based governance_risk: base 30 + overrides * 15 + days_pending penalty
- Composite score: weighted sum (cost 30%, schedule 25%, progress 25%, governance 20%)
- Categories: LOW, MODERATE, HIGH, VERY_HIGH, CRITICAL

**ML Integration Hooks**:
- Function accepts ml_cost_risk and ml_schedule_risk parameters
- Uses ML outputs if available, otherwise falls back to rule-based
- Returns ml_model_status and ml_model_version in result

**Gaps**:
- ML parameters not being passed from API layer
- No ML inference call in risk computation pipeline
- SHAP not integrated

---

### Existing Database Schema

**predictions table** (backend/app/models/predictions.py):
- prediction_id (PK)
- project_id (FK)
- model_version
- prediction_type
- predicted_value
- confidence_interval_low
- confidence_interval_high
- shap_values (JSONB)
- prediction_timestamp

**Status**: Schema supports ML predictions, but not being used

---

## 5. FEATURE SAFETY ANALYSIS

### Available CUF Fields (No Future Leakage):
- sanctioned_cost (from project)
- revised_cost (from latest submission)
- expenditure (from latest submission)
- physical_progress (from latest submission)
- planned_completion (from latest submission)
- sector (from project)
- state (from project)
- approved_date (from project)
- reporting_month (from submission)
- submitted_at (from submission)

### Derived Features (Safe):
- completion_by_expenditure = expenditure / sanctioned_cost
- completion_by_progress = physical_progress / 100
- log_sanctioned_cost = log(sanctioned_cost)
- size_band = function of sanctioned_cost
- cost_revision_ratio = revised_cost / sanctioned_cost

### One-Hot Encoding (Safe):
- sector one-hot (from project.sector)
- size_band one-hot (from derived size_band)
- state one-hot (from project.state)

### Unavailable/Not Used:
- agency_track_record (not in PAIMANA data)
- nqc_score (not in PAIMANA data)
- ppi_percentile (computed by PBE, not in training)
- progress_velocity_3m (requires 3-month history, not in current inference)
- cost_revision_count (requires full history, not in current inference)
- reporting_lag_days (available but not in training features)
- expenditure_to_progress_gap (available but not in training features)
- schedule_slip_months (available but not in training features)

### Feature Safety Conclusion:
**All training features are safe from future leakage**. They use only:
- Project static attributes (sector, state, sanctioned_cost, approved_date)
- Latest submission data (revised_cost, expenditure, physical_progress, planned_completion)
- Derived ratios and transforms of the above

No future information (final outcomes, future submissions) is used in features.

---

## 6. SHAP EXPLAINABILITY STATUS

### Existing SHAP Infrastructure (backend/app/services/shap_explainer.py)

**Status**: Partially implemented

**Current Capabilities**:
- SHAP TreeExplainer for XGBoost and LightGBM
- explain_with_shap() function for ML models
- Rule-based fallback for non-ML risk
- Top 5 feature contributions with direction
- Human-readable feature labels
- Feature explanations

**Gaps**:
- Not integrated into ML inference service
- Not called during risk computation
- SHAP values not persisted to database
- SHAP not exposed in API response for actual risk

**SHAP Summary from Training** (shap_summary_v2.json):
- Cost XGBoost top features: completion_by_expenditure (1.88), log_sanctioned_cost (0.85), sector_Transmission & Distribution (0.15)
- Schedule LightGBM top features: completion_by_progress (0.15), state_Gujarat (0.14), state_Maharashtra (0.10)

---

## 7. PREPROCESSING REQUIREMENTS

### From Training Pipeline:

**No Scalers/Encoders Found**:
- Models appear to use raw features without scaling
- One-hot encoding done during training
- No StandardScaler, MinMaxScaler, or other transformers found
- No encoder objects saved with models

**Implication**:
- Inference must replicate one-hot encoding exactly as training
- No scaler transformation needed
- Feature names must match exactly (including one-hot columns)

---

## 8. TARGET LABELS

### Cost Overrun Target:
- **Name**: cost_overrun_10pct
- **Definition**: final_cost > sanctioned_cost * 1.10
- **Binary**: 1 if > 10% overrun, 0 otherwise
- **Training Prevalence**: 50.4%

### Schedule Delay Target:
- **Name**: delay_gt_6_months
- **Definition**: revised_completion_date - original_completion_date > 6 months
- **Binary**: 1 if > 6 months delay, 0 otherwise
- **Training Prevalence**: 71%

---

## 9. LIMITATIONS

### Model Limitations (from model_registry.json):
- Status: EXPERIMENTAL (not production validated)
- Training data: 454 completed projects (limited sample size)
- Calibration: Uncalibrated (probabilities not calibrated)
- No online learning (models not updated with new data)
- Geographic dominance: State features have high SHAP values (potential overfitting)

### Data Limitations:
- Many projects have "Unknown" sector (baseline category)
- State coverage limited to 10-11 states in training
- Size band coverage limited to 5 bands
- No agency reliability data
- No contractor data

### Infrastructure Limitations:
- Current inference service uses wrong feature names
- No one-hot encoding in inference
- No feature engineering in inference
- SHAP not integrated into risk pipeline
- ML predictions not persisted to database

---

## 10. INTEGRATION REQUIREMENTS

### Must Implement:
1. **Feature Engineering Service**: Extract and transform features from CUF data
2. **One-Hot Encoding**: Replicate training encoding for sector, size_band, state
3. **ML Inference Service**: Load models, construct features, predict probabilities
4. **SHAP Integration**: Generate SHAP explanations for predictions
5. **Hybrid Risk Engine**: Combine ML predictions with rule-based signals
6. **Database Persistence**: Store ML predictions with provenance
7. **API Extension**: Expose ML predictions in risk endpoint
8. **Frontend Update**: Display ML predictions and SHAP explanations

### Feature Mapping (Training → Database):
- sanctioned_cost → projects.sanctioned_cost
- revised_cost → cuf_submissions.revised_cost
- expenditure → cuf_submissions.expenditure
- physical_progress → cuf_submissions.physical_progress
- sector → projects.sector
- state → projects.state
- approved_date → projects.approved_date
- planned_completion → cuf_submissions.planned_completion
- reporting_month → cuf_submissions.reporting_month

### Derived Feature Calculations:
- completion_by_expenditure = expenditure / sanctioned_cost
- completion_by_progress = physical_progress / 100
- log_sanctioned_cost = log(sanctioned_cost)
- size_band = size_band_for_cost(sanctioned_cost)
- cost_revision_ratio = revised_cost / sanctioned_cost

---

## 11. RECOMMENDATIONS

### Immediate (P0):
1. Build production ML inference service with correct feature engineering
2. Implement one-hot encoding for sector, size_band, state
3. Integrate ML predictions into risk scoring pipeline
4. Add SHAP explainability to ML predictions
5. Persist ML predictions to database with provenance

### Short-term (P1):
1. Add model comparison utility (rule-based vs ML)
2. Implement ML risk trend tracking
3. Add early warning based on ML probability changes
4. Calibrate ML probabilities (isotonic regression or Platt scaling)

### Long-term (P2):
1. Implement online learning (model retraining on new data)
2. Add more features (agency reliability, contractor performance)
3. Expand state/sector coverage in training
4. Implement ensemble methods (combine multiple models)

---

**Audit Completed**: September 1, 2026  
**Auditor**: Cascade AI Assistant  
**Next Step**: Build production ML inference service
