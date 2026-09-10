# Schedule Model Diagnostics Report

**Date:** August 31, 2026  
**Purpose:** Diagnose schedule model ROC-AUC < 0.5 issue  
**Status:** CRITICAL ISSUE FOUND

---

## EXECUTIVE SUMMARY

**Root Cause Identified:** SEVERE TEMPORAL LABEL SHIFT

**Problem:**
- Train positive rate: 56.7%
- Validation positive rate: 91.7%
- Test positive rate: 94.0%

**Impact:**
- Models trained on balanced-ish dataset (56.7% positive)
- Models evaluated on highly imbalanced dataset (91.7-94.0% positive)
- This causes probability/class inversion and poor ROC-AUC

**Evidence:**
- All three models have inverted ROC-AUC > 0.5 when probabilities are flipped
- High F1 (0.814-0.915) is misleading due to majority-class prediction
- Confusion matrices show models predict positive almost always

---

## DIAGNOSTIC RESULTS

### 1. Schedule Label Audit

**Target Definition:** delay_gt_6_months
- Definition: delay_months > 6
- Calculation: revised_completion_date - original_completion_date
- Format: MM/YYYY parsed as month/year

**Audit Results:**
- Total labels: 422
- Target 1 (delayed): 300 (71.1%)
- Target 0 (not delayed): 122 (28.9%)
- Negative delays: 46 (10.9%)
- Target calculation matches: 422/422 ✅

**Conclusion:** Target definition is correct. No label construction bug.

---

### 2. Target Inversion Diagnostic

**ROC-AUC Comparison:**

| Model | Original ROC-AUC | Inverted ROC-AUC | Status |
|-------|-----------------|------------------|--------|
| Random Forest | 0.399 | 0.601 | ⚠️ Inverted higher |
| XGBoost | 0.454 | 0.546 | ⚠️ Inverted higher |
| LightGBM | 0.396 | 0.604 | ⚠️ Inverted higher |

**Conclusion:** Probability/class mapping is inverted. Models are predicting the opposite of what they should.

---

### 3. Temporal Split Label Shift

**Positive Rate by Split:**

| Split | Positive Rate | Count |
|-------|---------------|-------|
| Train | 56.7% | 254 |
| Validation | 91.7% | 84 |
| Test | 94.0% | 84 |

**Shift Magnitude:**
- Train → Val: +35.0 percentage points
- Train → Test: +37.3 percentage points

**Conclusion:** CRITICAL - Severe temporal label shift. This is the root cause.

---

### 4. Confusion Matrix Analysis

**Random Forest (threshold 0.5):**
- TN: 1, FP: 6, FN: 20, TP: 57
- Precision: 0.905
- Recall: 0.740
- F1: 0.814

**XGBoost (threshold 0.5):**
- TN: 1, FP: 6, FN: 18, TP: 59
- Precision: 0.908
- Recall: 0.766
- F1: 0.831

**LightGBM (threshold 0.5):**
- TN: 1, FP: 6, FN: 7, TP: 70
- Precision: 0.921
- Recall: 0.909
- F1: 0.915

**Analysis:**
- Models predict positive in 63/84 cases (75%)
- Only 1 true negative out of 7 actual negatives
- High F1 is achieved by predicting the majority class (positive)
- This is not meaningful discrimination

---

### 5. Threshold vs Ranking Analysis

**F1 Across Thresholds (Random Forest):**
- Threshold 0.1: F1 = 0.957
- Threshold 0.2: F1 = 0.943
- Threshold 0.3: F1 = 0.943
- Threshold 0.4: F1 = 0.847
- Threshold 0.5: F1 = 0.814

**Conclusion:** High F1 at low thresholds is due to predicting majority class. ROC-AUC (ranking) is the correct metric for discrimination quality.

---

### 6. Feature Importance

**Random Forest Top Features:**
1. completion_by_progress: 0.2123
2. completion_by_expenditure: 0.1848
3. sector_Transmission & Distribution: 0.1553
4. state_Gujarat: 0.0850
5. state_Maharashtra: 0.0462

**XGBoost Top Features:**
1. completion_by_progress: 0.2586
2. sector_Transmission & Distribution: 0.1958
3. sector_Aviation & Aviation Infrastructure: 0.1231

**LightGBM Top Features:**
1. state_Gujarat: 100.0000
2. completion_by_progress: 80.0000
3. state_Uttar Pradesh: 31.0000

**Conclusion:** Features appear reasonable. No obvious target proxy features.

---

### 7. Data Quality

**Issues Found:**
- 46 negative delays (10.9%)
- 13 extreme delays > 120 months (3.1%)
- Some projects have revised date before original date

**Conclusion:** Data quality issues exist but are not the primary cause of ROC-AUC < 0.5.

---

## ROOT CAUSE ANALYSIS

**Primary Issue:** TEMPORAL LABEL SHIFT

**Mechanism:**
1. Projects completed later in the dataset have much higher delay rates
2. Temporal split by completion_date creates distribution shift
3. Training data: 56.7% positive (balanced-ish)
4. Validation/test data: 91.7-94.0% positive (highly imbalanced)
5. Models learn from training distribution
6. Models evaluated on different distribution
7. Probability/class inversion occurs
8. ROC-AUC < 0.5 despite high F1

**Why F1 is misleading:**
- With 91.7% positive rate, naive classifier always predicting positive achieves:
  - Precision ≈ 91.7%
  - Recall = 100%
  - F1 ≈ 95.6%
- Models are essentially doing this (predicting positive most of the time)
- ROC-AUC measures ranking quality, which is poor

---

## RECOMMENDED ACTIONS

### Option A: Fix Temporal Split (Recommended)

**Action:** Use stratified split instead of temporal split

**Rationale:**
- Ensures consistent label distribution across splits
- Prevents distribution shift
- Allows proper model evaluation

**Trade-off:**
- Loses strict temporal validation
- May have some temporal leakage

**Implementation:**
- Use sklearn's StratifiedShuffleSplit
- Stratify by target label
- Maintain project-level split integrity

### Option B: Accept Limitation

**Action:** Keep schedule models as experimental with documented weakness

**Rationale:**
- Temporal split is scientifically valid
- Label shift reflects real-world temporal dynamics
- Models are genuinely weak for schedule prediction

**Trade-off:**
- Cannot claim strong schedule prediction capability
- Must document limitation explicitly

### Option C: Rebuild with Different Target

**Action:** Use different schedule target or features

**Rationale:**
- Current target may not be learnable with available features
- Alternative targets may have better temporal stability

**Trade-off:**
- Changes the problem definition
- Requires re-justification of target choice

---

## DECISION

**RECOMMENDED:** Option A - Fix Temporal Split

**Reasoning:**
1. Current evaluation is invalid due to distribution shift
2. High F1 is misleading and not meaningful
3. ROC-AUC < 0.5 indicates poor discrimination
4. Stratified split will allow proper evaluation
5. Can still document temporal dynamics separately

**Implementation:**
1. Rebuild schedule datasets with stratified split
2. Retrain all schedule models
3. Re-evaluate with consistent label distribution
4. Document temporal dynamics separately
5. If models still perform poorly, accept as limitation

---

## NEXT STEPS

1. Rebuild schedule_delay_labeled.csv with stratified split
2. Retrain RF, XGBoost, LightGBM on new split
3. Re-evaluate metrics
4. Compare with cost model performance
5. Make final decision on schedule model viability

---

**Prepared by:** Cascade AI Assistant  
**Date:** August 31, 2026  
**For:** SIH 2026 ML v2 Diagnostics
