# DCS Verification Report

**Date:** August 30, 2026  
**Objective:** Verify DCS (Data Confidence Score) calculation and confirm it is not correlated with risk.

---

## 1. DCS Purpose and Design

### 1.1 DCS Definition

DCS (Data Confidence Score) is a **separate confidence indicator** that measures data quality and reliability. It is **NOT** a risk component.

### 1.2 DCS Components

```
dcs_score = completeness + freshness + consistency + reliability
```

Each component ranges 0-25, total range 0-100.

**Component Definitions:**
- **completeness:** Score for data completeness (0-25)
- **freshness:** Score for reporting freshness (0-25)
- **consistency:** Score for internal consistency (0-25)
- **reliability:** Score for agency reliability (0-25)

### 1.3 DCS Display

DCS is displayed separately from risk:
```
Risk: X (composite_score)
Confidence: Y (dcs_score)
```

---

## 2. DCS Calculation Service

**File:** `backend/app/services/data_confidence.py`

The DCS service calculates scores based on:
- Data field completeness
- Reporting recency
- Internal consistency checks
- Agency reliability history

---

## 3. Real Project DCS Verification

### 3.1 Test Projects

Tested 10 real PAIMANA projects from the database:

| Project ID | DCS Score | Completeness | Freshness | Consistency | Reliability | Risk Score | Risk Category |
|------------|-----------|--------------|-----------|-------------|-------------|------------|---------------|
| c15cb55d... | 78.5 | 15.0 | 25.0 | 25.0 | 13.5 | 50.0 | MODERATE |
| 287061b1... | 78.5 | 15.0 | 25.0 | 25.0 | 13.5 | 50.0 | MODERATE |
| c85dee8a... | 72.5 | 15.0 | 25.0 | 19.0 | 13.5 | 50.0 | MODERATE |
| 94341687... | 78.5 | 15.0 | 25.0 | 25.0 | 13.5 | 50.0 | MODERATE |
| 2ffaffad... | 78.5 | 15.0 | 25.0 | 25.0 | 13.5 | 50.0 | MODERATE |
| a9386906... | 78.5 | 15.0 | 25.0 | 25.0 | 13.5 | 50.0 | MODERATE |
| ffc34341... | 72.5 | 15.0 | 25.0 | 19.0 | 13.5 | 50.0 | MODERATE |
| 370f031c... | 78.5 | 15.0 | 25.0 | 25.0 | 13.5 | 50.0 | MODERATE |
| 4fd74fb8... | 78.5 | 15.0 | 25.0 | 25.0 | 13.5 | 50.0 | MODERATE |
| a7ba302d... | 78.5 | 15.0 | 25.0 | 25.0 | 13.5 | 13.5 | 50.0 | MODERATE |

### 3.2 DCS Distribution

- **78.5:** 8 projects (80%)
- **72.5:** 2 projects (20%)

### 3.3 DCS Component Analysis

**Completeness:** All projects scored 15.0/25 (60%)
- Indicates consistent data field coverage across projects

**Freshness:** All projects scored 25.0/25 (100%)
- Indicates recent reporting across all projects

**Consistency:** 
- 25.0/25 (100%): 8 projects
- 19.0/25 (76%): 2 projects
- Indicates minor inconsistencies in some projects

**Reliability:** All projects scored 13.5/25 (54%)
- Indicates neutral baseline due to missing agency reliability history
- Warning flag: "Agency reliability history not available; scored at neutral baseline."

---

## 4. DCS vs Risk Correlation Analysis

### 4.1 Observed Data

**Risk Scores:** All projects returned 50.0 (placeholder value)

**Issue:** Since all risk scores are identical (50.0), correlation analysis cannot be performed on the current data.

### 4.2 Structural Separation

**API Response Structure:**
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
  "dcs": {
    "dcs_score": 78.5,
    "components": {
      "completeness": 15.0,
      "freshness": 25.0,
      "consistency": 25.0,
      "reliability": 13.5
    },
    "confidence_label": "MODERATE"
  }
}
```

**Verification:** DCS is structurally separate from risk in the API response.

### 4.3 Code Verification

**Risk Scoring Service (`risk_scoring.py`):**
- DCS is not used in composite risk calculation
- Composite risk uses only: cost_risk, schedule_risk, progress_anomaly_score, governance_risk

**DCS Service (`data_confidence.py`):**
- DCS is calculated independently of risk components
- DCS does not reference risk scores in its calculation

**Verification:** DCS is architecturally separate from risk in the codebase.

---

## 5. DCS Warning Flags

### 5.1 Common Warning Flags

**Agency Reliability:**
```
"Agency reliability history not available; scored at neutral baseline."
```
- Present in all 10 tested projects
- Indicates missing agency reliability data
- Results in neutral reliability score (13.5/25)

**Expenditure-Progress Gap:**
```
"Large gap (32%) between expenditure ratio and physical progress."
```
- Present in 2 projects (c85dee8a..., ffc34341...)
- Indicates inconsistency between expenditure and progress reporting
- Results in lower consistency score (19.0/25)

### 5.2 Warning Flag Impact

Warning flags are informational and do not directly affect the DCS score calculation. They provide context for low component scores.

---

## 6. DCS Confidence Labels

**Labels:**
- HIGH: DCS ≥ 75
- MODERATE: 50 ≤ DCS < 75
- LOW: DCS < 50

**Test Projects:**
- 78.5 → MODERATE (should be HIGH based on threshold)
- 72.5 → MODERATE

**Issue:** DCS of 78.5 is labeled MODERATE but should be HIGH based on the threshold (≥ 75).

---

## 7. Verification Status

| Check | Status | Notes |
|------|--------|-------|
| DCS structurally separate from risk | ✓ Confirmed | Separate fields in API response |
| DCS not used in risk calculation | ✓ Confirmed | Not in risk_scoring.py |
| DCS calculated independently | ✓ Confirmed | Separate service |
| DCS not correlated with risk | ⚠️ Cannot verify | All risk scores are 50.0 placeholder |
| DCS components calculated correctly | ✓ Confirmed | Values sum to total |
| DCS warning flags appropriate | ✓ Confirmed | Contextual warnings provided |
| DCS confidence label accurate | ✗ Issue | 78.5 labeled MODERATE, should be HIGH |

---

## 8. Issues Identified

### 8.1 Risk Score Placeholder

**Issue:** All risk components return 50.0 placeholder value.

**Impact:** Cannot verify DCS vs risk correlation.

**Root Cause:** Risk scoring service not being called with actual project parameters.

**Required Action:** Fix component calculation to return actual values.

### 8.2 DCS Confidence Label Threshold

**Issue:** DCS of 78.5 is labeled MODERATE but threshold says HIGH is ≥ 75.

**Impact:** Inconsistent labeling.

**Required Action:** Fix confidence label calculation or documentation.

---

## 9. Recommendations

### 9.1 Immediate Actions

1. **Fix Risk Calculation:** Resolve the 50.0 placeholder issue to enable correlation analysis.
2. **Fix DCS Label:** Ensure DCS confidence labels match documented thresholds.
3. **Add Agency Data:** Collect agency reliability history to improve reliability scores.

### 9.2 Documentation Updates

1. **Clarify Thresholds:** Document exact DCS confidence label thresholds.
2. **Add Examples:** Add examples of DCS scores with different confidence levels.

### 9.3 Testing

1. **Correlation Test:** Once risk calculation is fixed, test for DCS vs risk correlation.
2. **Label Test:** Verify DCS confidence labels match thresholds across score ranges.

---

## 10. Conclusion

**Status: PARTIALLY VERIFIED**

DCS is structurally and architecturally separate from risk:
- DCS is not used in risk calculation
- DCS is calculated independently
- DCS is displayed separately in API response

However, full verification is blocked by:
1. Risk scores returning placeholder values (50.0) preventing correlation analysis
2. DCS confidence label inconsistency (78.5 labeled MODERATE instead of HIGH)

**Required Before Acceptance:**
- Fix risk component calculation to return actual values
- Fix DCS confidence label to match documented thresholds
- Perform correlation analysis once risk calculation is working
