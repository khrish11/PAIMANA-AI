# Target Definitions for PAIMANA Experimental ML

## Overview

This document defines all supervised learning targets used for experimental model training on PAIMANA real data.

**IMPORTANT:** These targets are for experimental models only. The dataset has limited completed outcomes (160 projects with valid final labels), so results are not production-validated.

---

## TARGET A: Cost Overrun

### Definition

**cost_overrun_ratio = final_cost / sanctioned_cost - 1**

Where:
- `sanctioned_cost`: original_cost_crore (or revised_cost_crore if original unavailable)
- `final_cost`: cumulative_expenditure_crore at project completion (100% progress)

### Binary Targets

| Target Name | Threshold | Description |
|-------------|-----------|-------------|
| `cost_overrun_5pct` | ratio > 0.05 | Cost exceeds sanctioned amount by >5% |
| `cost_overrun_10pct` | ratio > 0.10 | Cost exceeds sanctioned amount by >10% |
| `cost_overrun_20pct` | ratio > 0.20 | Cost exceeds sanctioned amount by >20% |

### Label Creation Rules

1. Only create labels for projects with 100% physical progress
2. Only create labels when both sanctioned_cost and final_cost are available
3. Only create labels when sanctioned_cost > 0
4. Projects not meeting these criteria are excluded from cost overrun targets

### Sample Size

- Total labeled projects: 160
- cost_overrun_5pct: 9.4% positive (15/160)
- cost_overrun_10pct: 9.4% positive (15/160)
- cost_overrun_20pct: 7.5% positive (12/160)

### Class Imbalance

- SEVERE: Only 9.4% positive class for 5pct/10pct thresholds
- SEVERE: Only 7.5% positive class for 20pct threshold
- Requires class weighting for all models

---

## TARGET B: Schedule Delay

### Definition

**delay_months = actual_completion_date - original_completion_date**

Where:
- `original_completion_date`: original_completion_date field (MM/YYYY format)
- `actual_completion_date`: revised_completion_date field (MM/YYYY format)

Dates are converted to months since epoch for calculation.

### Binary Targets

| Target Name | Threshold | Description |
|-------------|-----------|-------------|
| `delay_gt_3_months` | delay > 3 | Project delayed by >3 months |
| `delay_gt_6_months` | delay > 6 | Project delayed by >6 months |
| `delay_gt_12_months` | delay > 12 | Project delayed by >12 months |

### Label Creation Rules

1. Only create labels for projects with 100% physical progress
2. Only create labels when both original_completion_date and actual_completion_date are available
3. Only create labels when dates are valid (MM/YYYY format)
4. Projects not meeting these criteria are excluded from schedule delay targets

### Sample Size

- Total labeled projects: 160
- delay_gt_3_months: 66.2% positive (106/160)
- delay_gt_6_months: 59.4% positive (95/160)
- delay_gt_12_months: 41.9% positive (67/160)

### Class Imbalance

- MODERATE: 66.2% positive for 3-month threshold
- MODERATE: 59.4% positive for 6-month threshold
- BALANCED: 41.9% positive for 12-month threshold

---

## TARGET C: Early Warning

### Definition

Early warning targets use **future information only for label creation**, while features use only historical/current information.

### Future Cost Revision

**future_3m_cost_revision**: Whether cost increases materially (>10%) during months N+1 to N+3

**future_6m_cost_revision**: Whether cost increases materially (>10%) during months N+1 to N+6

Calculation:
```
cost_increase = (max_future_cost - current_cost) / current_cost
future_Xm_cost_revision = 1 if cost_increase > 0.10 else 0
```

### Future Progress Stall

**future_3m_progress_stall**: Whether average progress velocity < 2% per month over next 3 months

**future_6m_progress_stall**: Whether average progress velocity < 2% per month over next 6 months

Calculation:
```
total_change = progress[N+X] - progress[N]
avg_velocity = total_change / X
future_Xm_progress_stall = 1 if avg_velocity < 2.0 else 0
```

### Label Creation Rules

1. Labels are created for each monthly observation where future data exists
2. Future data is used ONLY for label creation, NEVER as features
3. If insufficient future data exists (<2 observations), label is set to None
4. Current period features are used for prediction

### Sample Size

- Total labeled observations: 17,556
- future_3m_cost_revision: 2.8% positive (492/17,556)
- future_3m_progress_stall: 83.5% positive (14,659/17,556)

### Class Imbalance

- SEVERE: Only 2.8% positive for cost revision target
- SEVERE: 83.5% positive for progress stall target
- Requires class weighting for all models

---

## Temporal Leakage Protection

### Feature Constraints

All features for month N must use only information available by month N:

- ✅ Current cost, expenditure, progress
- ✅ Historical averages up to month N
- ✅ Historical trends up to month N
- ❌ Future cost revisions
- ❌ Future progress values
- ❌ Future completion dates

### Label Constraints

Labels may use future information ONLY for label creation:

- ✅ Future cost revisions for label
- ✅ Future progress for label
- ❌ Future information as features

### July 2026 Holdout

July 2026 data is reserved as final holdout and excluded from all training/validation.

---

## Recommended Targets for Experimental Training

Given the sample sizes and class imbalance:

1. **Primary Target: delay_gt_6_months**
   - 160 labeled projects
   - 59.4% positive (moderate imbalance)
   - Most balanced of the cost/schedule targets

2. **Secondary Target: future_3m_cost_revision**
   - 17,556 labeled observations
   - 2.8% positive (severe imbalance)
   - Requires strong class weighting
   - Good for early warning use case

3. **Exploratory Target: cost_overrun_10pct**
   - 160 labeled projects
   - 9.4% positive (severe imbalance)
   - Requires strong class weighting
   - Limited sample size

---

## Class Weighting Strategy

For all targets with severe class imbalance (<10% or >90% positive):

- **Random Forest**: `class_weight="balanced"`
- **XGBoost**: `scale_pos_weight = negative_count / positive_count`
- **LightGBM**: `is_unbalance=True` or custom class weights

For targets with moderate imbalance (30-70% positive):

- Use default class weights
- Monitor confusion matrix for bias

---

## Limitations

1. **Small sample size**: Only 160 projects have valid final cost/schedule labels
2. **Short time horizon**: 13 months insufficient for most projects to complete
3. **Class imbalance**: Most targets have severe class imbalance
4. **Extraction issues**: Some fields may have extraction errors affecting label quality
5. **Not production-validated**: These targets are for experimental models only

---

## Version History

- v1.0 (2026-08-28): Initial target definitions for experimental ML training
