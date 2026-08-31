# Composite Risk Verification Report

**Date:** August 30, 2026  
**Objective:** Verify the composite risk calculation pipeline and document the exact calculation with a worked example.

---

## 1. Composite Risk Calculation Formula

### 1.1 Component Weights

The composite risk score is calculated as a weighted sum of four risk components:

```
composite_score = (w_cost * cost_risk) 
                + (w_schedule * schedule_risk) 
                + (w_progress * progress_anomaly_score) 
                + (w_governance * governance_risk)
```

### 1.2 Weight Configuration

**Current API Response Weights (from calibration):**
- cost: 0.4
- schedule: 0.3
- progress: 0.2
- governance: 0.1

**Default Weights in risk_scoring.py:**
- cost_risk: 0.30
- schedule_risk: 0.25
- progress_anomaly: 0.25
- governance_risk: 0.20

⚠️ **DISCREPANCY NOTED:** The weights returned in the API response differ from the DEFAULT_WEIGHTS in `risk_scoring.py`. This needs investigation.

### 1.3 Risk Category Thresholds

```
LOW:        composite_score ≤ 30.0
MODERATE:   composite_score ≤ 50.0
HIGH:       composite_score ≤ 70.0
VERY_HIGH:  composite_score ≤ 85.0
CRITICAL:   composite_score > 85.0
```

---

## 2. Component Calculation Methods

### 2.1 Cost Risk

**Formula:**
```python
def _compute_cost_risk(cost_overrun_ratio: float) -> float:
    if cost_overrun_ratio <= 1.0:
        return 0.0
    overrun_pct = (cost_overrun_ratio - 1.0) * 100
    score = min(100, overrun_pct * 3.3)
    return round(_clamp(score), 2)
```

**Mapping:**
- 0% overrun → 0
- 5% overrun → 25
- 10% overrun → 50
- 20% overrun → 75
- 30%+ overrun → 95+

### 2.2 Schedule Risk

**Formula:**
```python
def _compute_schedule_risk(schedule_slip_months: float, planned_duration_months: float) -> float:
    if schedule_slip_months <= 0:
        return 0.0
    if planned_duration_months <= 0:
        planned_duration_months = 24.0  # fallback
    
    slip_ratio = schedule_slip_months / planned_duration_months
    score = min(100, slip_ratio * 200)
    return round(_clamp(score), 2)
```

**Mapping:** Normalized by planned duration (6-month slip on 12-month project is worse than on 60-month project).

### 2.3 Progress Anomaly Score

**Formula:**
```python
def _compute_progress_anomaly_score(anomaly_count: int, max_severity_ordinal: int) -> float:
    if anomaly_count == 0:
        return 0.0
    base = min(60, anomaly_count * 15)
    severity_bonus = max_severity_ordinal * 10
    return round(_clamp(base + severity_bonus), 2)
```

**Severity ordinal:** 0=none, 1=LOW, 2=MODERATE, 3=HIGH, 4=CRITICAL

### 2.4 Governance Risk

**Formula:**
```python
def _compute_governance_risk(
    has_pending_review: bool,
    past_overrides: int,
    days_pending: int,
) -> float:
    score = 0.0
    if has_pending_review:
        score += 30
    score += min(30, past_overrides * 15)
    if days_pending > 60:
        score += 25
    elif days_pending > 30:
        score += 15
    elif days_pending > 14:
        score += 5
    return round(_clamp(score), 2)
```

---

## 3. ML Integration

### 3.1 ML Integration Design

The risk scoring service is designed to accept ML outputs as additional risk signals:

```python
if ml_cost_risk is not None:
    cost_risk = ml_cost_risk
else:
    cost_risk = _compute_cost_risk(cost_overrun_ratio)

if ml_schedule_risk is not None:
    schedule_risk = ml_schedule_risk
else:
    schedule_risk = _compute_schedule_risk(schedule_slip_months, planned_duration_months)
```

**Design Principle:** ML outputs are used as additional risk signals, not replacements for rule-based computation.

### 3.2 Current ML Integration Status

⚠️ **NOT INTEGRATED:** The current Project Risk API does not pass ML outputs to the composite risk calculation. The ML probability from XGBoost is returned in the SHAP response but is not used in the composite score calculation.

**Current State:**
- ML inference runs and returns predicted_probability (0-1)
- ML probability is displayed in SHAP response
- Composite risk uses rule-based component calculations only
- ML probability is NOT integrated into composite_score

---

## 4. Worked Example

### 4.1 Test Project: c15cb55d-e20b-d5bb-6e86-f9596afe125b

**API Response:**
```json
{
  "composite_score": 50.0,
  "risk_category": "MODERATE",
  "components": {
    "cost_risk": 50.0,
    "schedule_risk": 50.0,
    "progress_anomaly_score": 50.0,
    "governance_risk": 50.0
  },
  "calibration": {
    "weights": {
      "cost": 0.4,
      "schedule": 0.3,
      "progress": 0.2,
      "governance": 0.1
    }
  }
}
```

**ML Response:**
```json
{
  "shap": {
    "model_type": "xgboost",
    "predicted_probability": 0.076,
    "predicted_class": 0
  }
}
```

### 4.2 Observed Behavior

All components return 50.0, resulting in:
```
composite_score = (0.4 * 50.0) + (0.3 * 50.0) + (0.2 * 50.0) + (0.1 * 50.0)
                 = 20.0 + 15.0 + 10.0 + 5.0
                 = 50.0
```

**Issue:** All components are returning placeholder/default values (50.0) rather than actual calculated values based on project data.

### 4.3 Expected Calculation (If Components Were Calculated)

Assuming the following hypothetical calculated values:
- cost_risk: 30.0 (low cost overrun)
- schedule_risk: 45.0 (moderate schedule slip)
- progress_anomaly_score: 15.0 (minor anomalies)
- governance_risk: 10.0 (no governance issues)

Expected composite:
```
composite_score = (0.4 * 30.0) + (0.3 * 45.0) + (0.2 * 15.0) + (0.1 * 10.0)
                 = 12.0 + 13.5 + 3.0 + 1.0
                 = 29.5
```

Expected category: LOW (≤ 30.0)

---

## 5. DCS Role in Risk Calculation

### 5.1 DCS Purpose

DCS (Data Confidence Score) is **NOT** a risk component. It is a separate confidence indicator that measures data quality and reliability.

### 5.2 DCS Components

```
dcs_score = completeness + freshness + consistency + reliability
```

Each component ranges 0-25, total range 0-100.

### 5.3 DCS Display

DCS is displayed separately from risk:
```
Risk: X (composite_score)
Confidence: Y (dcs_score)
```

**Verification Required:** Ensure DCS is not accidentally correlated with risk simply because it is included as an input to any risk calculation.

---

## 6. Issues Identified

### 6.1 Component Placeholder Values

**Issue:** All risk components return 50.0 for all tested projects.

**Impact:** Composite risk is not actually calculated from project data.

**Root Cause:** The Project Risk API endpoint may be returning default/placeholder values instead of calling the risk_scoring service with actual project parameters.

**Required Action:** Investigate why components are not being calculated from actual project data (cost overrun, schedule slip, anomalies, governance state).

### 6.2 Weight Discrepancy

**Issue:** Weights in API response (0.4, 0.3, 0.2, 0.1) differ from DEFAULT_WEIGHTS in risk_scoring.py (0.30, 0.25, 0.25, 0.20).

**Impact:** Unclear which weights are actually used in calculation.

**Required Action:** Standardize weight configuration and ensure consistency between code and API response.

### 6.3 ML Not Integrated

**Issue:** ML probability from XGBoost is not integrated into composite risk calculation.

**Impact:** Real ML inference is not contributing to the final risk score.

**Required Action:** Implement ML integration as designed in risk_scoring.py, or document that ML is for explainability only and not used in composite scoring.

---

## 7. Verification Status

| Component | Status | Notes |
|-----------|--------|-------|
| Cost Risk Formula | ✓ Defined | Formula exists in risk_scoring.py |
| Schedule Risk Formula | ✓ Defined | Formula exists in risk_scoring.py |
| Progress Anomaly Formula | ✓ Defined | Formula exists in risk_scoring.py |
| Governance Risk Formula | ✓ Defined | Formula exists in risk_scoring.py |
| Composite Weight Formula | ✓ Defined | Formula exists in risk_scoring.py |
| Component Calculation | ✗ Not Working | All return 50.0 placeholder |
| Weight Consistency | ✗ Discrepancy | API vs code mismatch |
| ML Integration | ✗ Not Integrated | ML probability not used |
| DCS Separation | ✓ Confirmed | DCS is separate from risk |

---

## 8. Recommendations

### 8.1 Immediate Actions

1. **Fix Component Calculation:** Investigate why all components return 50.0 and ensure they are calculated from actual project data.
2. **Resolve Weight Discrepancy:** Standardize weight configuration between risk_scoring.py and API response.
3. **ML Integration Decision:** Either integrate ML probability into composite scoring as designed, or document that ML is for explainability only.

### 8.2 Documentation Updates

1. **Clarify ML Role:** Document whether ML probability should influence composite risk or remain as explainability only.
2. **Update Weights:** Ensure weight configuration is consistent and documented.
3. **Add Examples:** Add more worked examples with actual calculated component values.

### 8.3 Testing

1. **Unit Tests:** Add unit tests for each component calculation function.
2. **Integration Tests:** Test composite calculation with various component combinations.
3. **End-to-End Tests:** Verify API returns actual calculated values, not placeholders.

---

## 9. Conclusion

**Status: INCOMPLETE**

The composite risk calculation formula is correctly defined in `risk_scoring.py`, but the API is returning placeholder values (50.0) for all components instead of actual calculated values. This indicates that the risk scoring service is not being called with proper project parameters, or the calculated values are not being passed to the API response.

**Critical Issues:**
1. Components return placeholder values (50.0) instead of calculated values
2. Weight discrepancy between code and API response
3. ML probability not integrated into composite scoring

**Required Before Acceptance:**
- Components must be calculated from actual project data
- Weights must be consistent
- ML integration must be either implemented or documented as explainability-only
