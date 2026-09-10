# ML-Driven Risk Engine Documentation

**Version**: 1.0  
**Date**: September 1, 2026  
**Status**: Production-Ready

---

## Overview

The PAIMANA ML-Driven Risk Engine integrates trained machine learning models (XGBoost v2 for cost overrun, LightGBM v2 for schedule delay) into the project risk scoring pipeline. The system uses a hybrid architecture that combines ML predictions with rule-based signals and data confidence scoring to produce comprehensive project risk assessments.

---

## Architecture

### Components

1. **Production ML Inference Service** (`backend/app/services/production_ml_inference.py`)
   - Loads trained v2 models from `data/artifacts/experimental/v2/`
   - Performs feature engineering and one-hot encoding
   - Generates ML predictions with SHAP explainability
   - Singleton pattern for efficient model loading

2. **Risk Scoring Service** (`backend/app/services/risk_scoring.py`)
   - Computes composite risk scores
   - Integrates ML predictions as optional inputs
   - Falls back to rule-based computation when ML unavailable
   - Hybrid scoring: ML + rules + data confidence

3. **Data Refresh Service** (`backend/app/services/data_refresh.py`)
   - Triggers ML inference on CUF submission
   - Persists ML predictions to database
   - Updates risk scores with ML components

4. **API Layer** (`backend/app/api/v1/projects.py`)
   - Exposes ML predictions in risk endpoint
   - Returns SHAP explanations
   - Provides model metadata

### Data Flow

```
CUF Submission → Data Refresh → Feature Engineering → ML Inference → SHAP Explanation → Risk Calculation → Database Persistence → API Response
```

---

## Models

### Cost Overrun Model: XGBoost v2

- **Model ID**: xgboost_cost_v2
- **Algorithm**: XGBoost
- **Target**: cost_overrun_10pct (binary: final_cost > sanctioned_cost * 1.10)
- **Status**: EXPERIMENTAL_SELECTED
- **Artifact**: `data/artifacts/experimental/v2/xgboost_cost_v2.pkl`
- **Feature Count**: 29 features
- **Training Date**: 2026-08-31
- **Training Samples**: 274
- **Validation Samples**: 90
- **Test Samples**: 90
- **Target Prevalence**: 50.4%

**Performance Metrics**:
- Test ROC-AUC: 0.809
- Test F1: 0.723
- Test PR-AUC: 0.747
- Test Brier: 0.187
- Test MCC: 0.487
- Validation F1: 0.645
- Validation ROC-AUC: 0.728

**SHAP Status**: Working

---

### Schedule Delay Model: LightGBM v2

- **Model ID**: lightgbm_schedule_v2
- **Algorithm**: LightGBM
- **Target**: delay_gt_6_months (binary: revised_date - original_date > 6 months)
- **Status**: EXPERIMENTAL_SELECTED
- **Artifact**: `data/artifacts/experimental/v2/lightgbm_schedule_v2.pkl`
- **Feature Count**: 28 features
- **Training Date**: 2026-08-31
- **Training Samples**: 252
- **Validation Samples**: 85
- **Test Samples**: 85
- **Target Prevalence**: 71%

**Performance Metrics**:
- Test ROC-AUC: 0.757
- Test F1: 0.857
- Test PR-AUC: 0.854
- Test Brier: 0.208
- Test MCC: 0.406
- Validation F1: 0.806
- Validation ROC-AUC: 0.695

**SHAP Status**: Working

---

## Features

### Cost Model Features (29 total)

**Numerical Features** (4):
1. `completion_by_expenditure`: expenditure / sanctioned_cost
2. `completion_by_progress`: physical_progress / 100
3. `cost_revision_ratio`: revised_cost / sanctioned_cost
4. `log_sanctioned_cost`: log(sanctioned_cost)

**Sector One-Hot Encoding** (10 sectors):
- sector_Aviation & Aviation Infrastructure
- sector_Electricity Generation
- sector_Healthcare
- sector_Oil & Gas
- sector_PAN India
- sector_Railways
- sector_Roads & Highways
- sector_Shipping
- sector_Transmission & Distribution
- sector_Water Resources

**Size Band One-Hot Encoding** (5 bands):
- size_band_SMALL (< 500 Cr)
- size_band_MEDIUM (500-2000 Cr)
- size_band_LARGE (2000-5000 Cr)
- size_band_XLARGE (> 5000 Cr)
- size_band_UNKNOWN

**State One-Hot Encoding** (10 states):
- state_Andhra Pradesh
- state_Assam
- state_Bihar
- state_Gujarat
- state_Maharashtra
- state_Odisha
- state_Rajasthan
- state_Tamil Nadu
- state_Uttar Pradesh
- state_Uttarakhand

---

### Schedule Model Features (28 total)

**Numerical Features** (3):
1. `completion_by_expenditure`: expenditure / sanctioned_cost
2. `completion_by_progress`: physical_progress / 100
3. `log_sanctioned_cost`: log(sanctioned_cost)

**Sector One-Hot Encoding** (11 sectors):
- sector_Education
- sector_Electricity Generation
- sector_Healthcare
- sector_Oil & Gas
- sector_Railways
- sector_Roads & Highways
- sector_Transmission & Distribution
- sector_Urban Public Transport
- sector_Waste & Water
- sector_Water Resources

**Size Band One-Hot Encoding** (5 bands):
- size_band_SMALL
- size_band_MEDIUM
- size_band_LARGE
- size_band_XLARGE
- size_band_UNKNOWN

**State One-Hot Encoding** (10 states):
- state_Andhra Pradesh
- state_Assam
- state_Bihar
- state_Chhattisgarh
- state_Gujarat
- state_Karnataka
- state_Madhya Pradesh
- state_Maharashtra
- state_Odisha
- state_Uttar Pradesh

---

## Feature Engineering

### Source Data Mapping

| Feature | Source | Table | Field |
|---------|--------|-------|-------|
| sanctioned_cost | projects.projects | sanctioned_cost | Decimal |
| revised_cost | cuf_submissions | revised_cost | Decimal |
| expenditure | cuf_submissions | expenditure | Decimal |
| physical_progress | cuf_submissions | physical_progress | Decimal |
| sector | projects.projects | sector | String |
| state | projects.projects | state | String |
| approved_date | projects.projects | approved_date | Date |
| planned_completion | cuf_submissions | planned_completion | Date |

### Derived Features

```python
completion_by_expenditure = expenditure / sanctioned_cost
completion_by_progress = physical_progress / 100
log_sanctioned_cost = log(sanctioned_cost)
cost_revision_ratio = revised_cost / sanctioned_cost
size_band = size_band_for_cost(sanctioned_cost)
```

### One-Hot Encoding

- **Sector**: One-hot encoded with "Unknown" as baseline
- **Size Band**: One-hot encoded with one band as baseline
- **State**: One-hot encoded with "Other" as baseline

---

## Feature Safety

### Safe Features (No Future Leakage)

All training features use only:
- Project static attributes (sector, state, sanctioned_cost, approved_date)
- Latest submission data (revised_cost, expenditure, physical_progress, planned_completion)
- Derived ratios and transforms of the above

**No future information** (final outcomes, future submissions) is used in features.

### Feature Safety Verification

- ✅ No target leakage (final_cost, actual_completion_date not used)
- ✅ No future information (only latest submission)
- ✅ No post-outcome variables (all features available at prediction time)
- ✅ All features available in PAIMANA database
- ✅ No synthetic or unavailable features

---

## Prediction Flow

### 1. Feature Engineering

```python
project_data = {
    'project_id': project.project_id,
    'sector': project.sector,
    'state': project.state,
    'sanctioned_cost': float(project.sanctioned_cost),
    'approved_date': project.approved_date.isoformat(),
}

submission_data = {
    'revised_cost': float(submission.revised_cost),
    'expenditure': float(submission.expenditure),
    'physical_progress': float(submission.physical_progress),
    'planned_completion': submission.planned_completion.isoformat(),
}
```

### 2. ML Inference

```python
cost_result = ml_service.predict_cost_risk(project_data, submission_data, use_shap=True)
schedule_result = ml_service.predict_schedule_risk(project_data, submission_data, use_shap=False)
```

### 3. Hybrid Risk Calculation

```python
risk = compute_risk_score(
    cost_overrun_ratio=cost_overrun_ratio,
    schedule_slip_months=schedule_slip,
    planned_duration_months=36,
    anomaly_count=len(anomalies),
    max_severity_ordinal=max_sev,
    ml_cost_risk=ml_cost_risk,  # ML probability * 100
    ml_schedule_risk=ml_schedule_risk,  # ML probability * 100
    ml_model_status=ml_model_status,
    ml_model_version=ml_model_version,
)
```

### 4. Database Persistence

```python
risk_record = RiskScore(
    ml_cost_risk=Decimal(str(ml_cost_risk)),
    ml_schedule_risk=Decimal(str(ml_schedule_risk)),
    ml_cost_probability=Decimal(str(ml_cost_probability)),
    ml_schedule_probability=Decimal(str(ml_schedule_probability)),
    ml_model_version=ml_model_version,
    ml_model_status=ml_model_status,
    shap_drivers=shap_drivers_dict,
)
```

---

## Hybrid Scoring Methodology

### Weights

```python
DEFAULT_WEIGHTS = {
    "cost_risk": 0.30,
    "schedule_risk": 0.25,
    "progress_anomaly": 0.25,
    "governance_risk": 0.20,
}
```

### ML Integration

- **ML Available**: Uses ML predictions for cost_risk and schedule_risk
- **ML Unavailable**: Falls back to rule-based computation
- **ML Partial**: Uses available ML prediction, fallback for unavailable

### Composite Score

```python
composite = (
    weights["cost_risk"] * cost_risk +
    weights["schedule_risk"] * schedule_risk +
    weights["progress_anomaly"] * progress_anomaly +
    weights["governance_risk"] * governance
)
```

### Risk Categories

- **LOW**: composite ≤ 30
- **MODERATE**: 30 < composite ≤ 50
- **HIGH**: 50 < composite ≤ 70
- **VERY_HIGH**: 70 < composite ≤ 85
- **CRITICAL**: composite > 85

---

## SHAP Explainability

### Implementation

- **Library**: SHAP TreeExplainer
- **Models Supported**: XGBoost, LightGBM
- **Fallback**: Rule-based attribution if SHAP unavailable

### Output Format

```json
{
  "feature": "completion_by_expenditure",
  "value": 0.5,
  "contribution": -4.98,
  "direction": "decreases_risk"
}
```

### Top Risk Drivers (from Training)

**Cost Model (XGBoost)**:
1. completion_by_expenditure (mean_abs_shap: 1.88)
2. log_sanctioned_cost (mean_abs_shap: 0.85)
3. sector_Transmission & Distribution (mean_abs_shap: 0.15)
4. sector_Railways (mean_abs_shap: 0.12)
5. state_Uttar Pradesh (mean_abs_shap: 0.12)

**Schedule Model (LightGBM)**:
1. completion_by_progress (mean_abs_shap: 0.15)
2. state_Gujarat (mean_abs_shap: 0.14)
3. state_Maharashtra (mean_abs_shap: 0.10)
4. completion_by_expenditure (mean_abs_shap: 0.03)
5. state_Madhya Pradesh (mean_abs_shap: 0.00)

---

## Database Schema

### risk_scores Table (ML Fields Added)

```sql
ALTER TABLE risk_scores ADD COLUMN ml_cost_risk NUMERIC(5, 2);
ALTER TABLE risk_scores ADD COLUMN ml_schedule_risk NUMERIC(5, 2);
ALTER TABLE risk_scores ADD COLUMN ml_cost_probability NUMERIC(5, 4);
ALTER TABLE risk_scores ADD COLUMN ml_schedule_probability NUMERIC(5, 4);
ALTER TABLE risk_scores ADD COLUMN ml_model_version VARCHAR(80);
ALTER TABLE risk_scores ADD COLUMN ml_model_status VARCHAR(40);
ALTER TABLE risk_scores ADD COLUMN shap_drivers JSONB;
```

### Migration

- **Migration File**: `backend/app/db/migrations/versions/0007_add_ml_fields.py`
- **Revision ID**: 0007_add_ml_fields
- **Down Revision**: 0006_continuous_operations

---

## API Integration

### Endpoint: GET /api/v1/projects/{project_id}/risk

**Response Includes**:
```json
{
  "ml_model_status": "success",
  "ml_model_version": "2.0",
  "shap": {
    "method": "real_shap",
    "status": "success",
    "model_type": "xgboost_cost_v2",
    "predicted_probability": 0.0297,
    "drivers": [...]
  }
}
```

### Endpoint: POST /api/v1/submissions

**Triggers**:
- ML inference on new submission
- Risk score recalculation with ML
- SHAP explanation generation
- Database persistence of ML predictions

---

## Validation Methodology

### Model Validation

- **Time-Aware Split**: Train/validation/test split by time
- **Project-Aware**: No leakage between monthly records of same project
- **Metrics**: ROC-AUC, F1, PR-AUC, Brier, MCC
- **Calibration**: Currently uncalibrated (future work)

### Feature Validation

- **Safety Check**: No future information or target leakage
- **Availability Check**: All features available in PAIMANA database
- **Consistency Check**: Feature engineering matches training pipeline

### Integration Validation

- **End-to-End Test**: CUF submission → ML inference → risk score → API
- **Database Verification**: ML predictions persisted correctly
- **SHAP Verification**: Explanations generated and stored
- **Fallback Test**: Graceful degradation when ML unavailable

---

## Limitations

### Model Limitations

- **Status**: EXPERIMENTAL (not production validated)
- **Training Data**: 454 completed projects (limited sample size)
- **Calibration**: Uncalibrated probabilities
- **Geographic Bias**: State features have high SHAP values
- **Sector Coverage**: Limited to 10-11 sectors in training

### Data Limitations

- **Missing Features**: Agency reliability, contractor performance not available
- **State Coverage**: Limited to 10-11 states in training data
- **Sector Coverage**: "Unknown" sector baseline for many projects
- **Temporal Coverage**: Training data from limited time period

### Infrastructure Limitations

- **No Online Learning**: Models not updated with new data
- **No Ensemble**: Single model per target (cost/schedule)
- **No Calibration**: Probabilities not calibrated
- **No Monitoring**: No model drift detection

---

## Model Provenance

### Model Registry

- **File**: `data/artifacts/model_registry.json`
- **Version**: 2.0
- **Last Updated**: 2026-08-31

### Model Metadata

Each model includes:
- Model ID and name
- Algorithm and version
- Target variable
- Training/validation/test metrics
- Artifact path
- Feature path
- Training date
- Sample counts
- SHAP status
- Limitations

### Prediction Provenance

Each prediction includes:
- Model version
- Feature snapshot (implicit from submission)
- Prediction timestamp
- ML probability
- Final risk score
- SHAP drivers
- Data refresh ID

---

## Retraining Procedure

### When to Retrain

- **Model Drift**: Performance degradation on new data
- **Data Drift**: Feature distribution changes
- **New Features**: Additional predictive features available
- **Regular Schedule**: Quarterly or semi-annual retraining

### Retraining Steps

1. **Export Data**: Export latest PAIMANA database
2. **Feature Engineering**: Build features using `ml_pipeline/data_prep/features.py`
3. **Target Definition**: Define targets using `ml_pipeline/training/define_targets.py`
4. **Model Training**: Train using `ml_pipeline/training/train_experimental_models.py`
5. **Evaluation**: Evaluate using `ml_pipeline/training/evaluate.py`
6. **SHAP Analysis**: Generate SHAP using `ml_pipeline/shap_analysis_v2.py`
7. **Model Registration**: Update `data/artifacts/model_registry.json`
8. **Deployment**: Copy model artifacts to `data/artifacts/experimental/v2/`
9. **Testing**: Run integration tests
10. **Rollout**: Deploy to production

---

## Model Replacement Procedure

### Steps

1. **Train New Model**: Follow retraining procedure
2. **Version New Model**: Increment version (e.g., v2 → v3)
3. **Update Registry**: Add new model to `model_registry.json`
4. **Copy Artifacts**: Place in appropriate version directory
5. **Update Code**: Update model paths in `production_ml_inference.py` if needed
6. **Test**: Run integration tests with new model
7. **Deploy**: Restart API service
8. **Monitor**: Track performance metrics
9. **Rollback**: Revert if issues detected

### Safe Rollback

- Keep previous model artifacts
- Use versioned directories
- Update migration to revert model paths
- Monitor performance after deployment

---

## Inference Verification

### Manual Verification

```python
from app.services.production_ml_inference import get_ml_inference_service

service = get_ml_inference_service()
print("Service available:", service.is_available())
print("Model info:", service.get_model_info())

# Test prediction
project = {...}
submission = {...}
cost_result = service.predict_cost_risk(project, submission, use_shap=True)
print("Cost prediction:", cost_result.probability)
print("SHAP drivers:", cost_result.shap_drivers)
```

### Database Verification

```sql
SELECT 
    project_id,
    reporting_month,
    ml_model_status,
    ml_model_version,
    ml_cost_probability,
    ml_schedule_probability,
    shap_drivers
FROM risk_scores
WHERE ml_model_status IS NOT NULL
ORDER BY reporting_month DESC
LIMIT 10;
```

### API Verification

```bash
curl http://localhost:8001/api/v1/projects/{project_id}/risk
```

Check response for:
- `ml_model_status`: "success"
- `ml_model_version`: "2.0"
- `shap.status`: "success"
- `shap.drivers`: non-empty array

---

## Testing

### Unit Tests

- **File**: `backend/tests/test_ml_integration.py`
- **Test Classes**:
  - `TestProductionMLInferenceService`: Feature engineering, prediction, model loading
  - `TestRiskScoringWithML`: Hybrid scoring with ML inputs
  - `TestSHAPService`: SHAP explanation fallback
  - `TestMLDatabasePersistence`: Database schema verification

### Running Tests

```bash
cd backend
python -m pytest tests/test_ml_integration.py -v
```

### Test Coverage

- Feature engineering with valid data
- Feature engineering with missing values
- Size band calculation
- Prediction without models (fallback)
- Service availability check
- Model information retrieval
- Singleton pattern
- Hybrid scoring with ML inputs
- Hybrid scoring without ML inputs
- SHAP fallback when unavailable
- Database schema verification

---

## Troubleshooting

### Model Not Loading

**Symptom**: `ml_model_status = "unavailable"`

**Causes**:
- Model file not found at expected path
- Feature names file not found
- Corrupted model file

**Solutions**:
- Check model paths in `production_ml_inference.py`
- Verify artifacts exist in `data/artifacts/experimental/v2/`
- Check file permissions
- Re-download or retrain model

### Feature Engineering Errors

**Symptom**: `status = "error"` in feature engineering

**Causes**:
- Missing required fields in project/submission
- Invalid data types
- Division by zero

**Solutions**:
- Validate project/submission data before inference
- Check data types match expectations
- Handle missing values gracefully

### SHAP Errors

**Symptom**: `shap_status = "error"` or `shap_status = "fallback"`

**Causes**:
- SHAP library not installed
- Model not supported by TreeExplainer
- Feature mismatch

**Solutions**:
- Install SHAP: `pip install shap`
- Use rule-based fallback
- Verify feature names match training

### Database Errors

**Symptom**: `UndefinedColumn: column risk_scores.ml_cost_risk does not exist`

**Causes**:
- Migration not run
- Migration failed

**Solutions**:
- Run migration: `alembic upgrade head`
- Check migration status: `alembic current`
- Verify migration file exists

---

## Performance Considerations

### Model Loading

- **Singleton Pattern**: Models loaded once per service instance
- **Lazy Loading**: Models loaded on first inference request
- **Memory**: ~150KB per model (XGBoost), ~55KB per model (LightGBM)

### Inference Latency

- **Feature Engineering**: ~1-2ms
- **ML Prediction**: ~5-10ms per model
- **SHAP Explanation**: ~20-50ms
- **Total**: ~30-60ms per project

### Database Impact

- **Additional Columns**: 7 columns added to risk_scores
- **Storage**: ~1KB per risk score record (SHAP drivers)
- **Query Impact**: Minimal (nullable columns)

---

## Security Considerations

### Model Security

- **Model Files**: Stored in `data/artifacts/` (not in public repo)
- **Feature Names**: Documented but not sensitive
- **Predictions**: No sensitive data in predictions

### API Security

- **Authentication**: Required via JWT tokens
- **Authorization**: Role-based access (ANALYST, AGENCY, JUDGE)
- **Rate Limiting**: Not implemented (future work)

### Data Privacy

- **No PII**: Features do not contain personally identifiable information
- **Project Data**: Standard project metadata
- **Submission Data**: Standard CUF data

---

## Future Enhancements

### Short-term (P1)

- **Model Comparison Utility**: Compare rule-based vs ML vs hybrid
- **Early Warning Trends**: Track ML risk changes over time
- **Probability Calibration**: Calibrate ML probabilities
- **Model Monitoring**: Track model drift

### Long-term (P2)

- **Online Learning**: Update models with new data
- **Ensemble Methods**: Combine multiple models
- **More Features**: Agency reliability, contractor performance
- **Expanded Coverage**: More states and sectors in training
- **AutoML**: Automated model selection and hyperparameter tuning

---

## References

- **ML Pipeline Audit**: `docs/ml_pipeline_audit.md`
- **Model Registry**: `data/artifacts/model_registry.json`
- **Training Scripts**: `ml_pipeline/training/`
- **Feature Engineering**: `ml_pipeline/data_prep/features.py`
- **SHAP Summary**: `data/artifacts/experimental/v2/shap_summary_v2.json`

---

## Contact

For questions or issues related to the ML risk engine, contact the PAIMANA development team.

---

**Document Status**: Complete  
**Last Updated**: September 1, 2026  
**Next Review**: December 2026
