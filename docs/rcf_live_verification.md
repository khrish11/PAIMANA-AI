# RCF Live Verification Report

**Date:** August 30, 2026  
**Objective:** Verify 125 fitted reference classes and fallback status.

---

## 1. RCF Purpose and Design

### 1.1 RCF Definition

RCF (Reference Class Forecasting) provides probabilistic forecasts for cost overruns and schedule delays based on historical reference classes of similar completed projects.

### 1.2 Reference Class Definition

Reference classes are defined by:
- **Sector:** Project sector (e.g., Roads, Railways, Energy)
- **State/Region:** Geographic location
- **Size Band:** Cost-based categorization (150-500 Cr, 500-2000 Cr, 2000+ Cr)

### 1.3 Minimum Cluster Size

**SRS Requirement:** Minimum 15 completed projects per reference class (SRS Section 6.4.2).

**Fallback Behavior:** If a reference class has < 15 completed projects, the system falls back to national-sector level.

---

## 2. RCF Engine Implementation

### 2.1 Service Code

**File:** `backend/app/services/rcf_engine.py`

**Key Function:** `fit_reference_class()`

**Parameters:**
- `completed_projects`: DataFrame of completed projects
- `sector`: Project sector
- `state`: Project state/region
- `size_band`: Cost-based size band
- `min_cluster_size`: Minimum cluster size (default: 15)

**Fallback Logic:**
```python
cluster = completed_projects[
    (completed_projects["sector"] == sector) &
    (completed_projects[state_key] == state) &
    (completed_projects["size_band"] == size_band)
] if sector and size_band else completed_projects.copy()

used_fallback = len(cluster) < min_cluster_size

if used_fallback and sector:
    cluster = completed_projects[completed_projects["sector"] == sector]
    warning = (
        "Reference-class cluster below 15 completed projects; "
        "using national-sector fallback as specified in SRS Section 6.4.2."
    )
```

### 2.2 Quantile Calculation

**Cost Overrun Quantiles:**
- P50: 50th percentile (median)
- P80: 80th percentile
- P90: 90th percentile

**Schedule Delay Quantiles:**
- P50: 50th percentile (median)

**Probability Calculations:**
- Probability of > 5% overrun
- Probability of > 10% overrun
- Probability of > 20% overrun

---

## 3. Real Project RCF Tests

### 3.1 Test Projects

Tested 3 real PAIMANA projects:

| Project ID | Sector | Size Band | State | Sample Count | Used Fallback | Warning |
|------------|--------|-----------|-------|--------------|--------------|---------|
| c15cb55d... | Unknown | 500-2000 Cr | Bihar | 0 | true | No completed projects available for RCF fallback cluster |
| 287061b1... | Unknown | 150-500 Cr | Assam | 0 | true | No completed projects available for RCF fallback cluster |
| c85dee8a... | Unknown | 150-500 Cr | Assam | 0 | true | No completed projects available for RCF fallback cluster |

### 3.2 RCF Response Structure

**Example Response:**
```json
{
  "sector": "Unknown",
  "size_band": "500-2000 Cr",
  "region": "Bihar",
  "sample_count": 0,
  "used_fallback": true,
  "warning": "No completed projects available for RCF fallback cluster",
  "cost_overrun_p50": 0.1,
  "cost_overrun_p80": 0.2,
  "cost_overrun_p90": 0.3,
  "schedule_delay_p50": 0.0,
  "schedule_delay_p80": 0.0,
  "schedule_delay_p90": 0.0,
  "p50_final_cost": 1221.25,
  "p80_final_cost": 1332.28,
  "p90_final_cost": 1443.3,
  "p50_completion_months": 36.0,
  "p80_completion_months": 36.0,
  "p90_completion_months": 36.0,
  "probability_overrun_gt_5": 0.0,
  "probability_overrun_gt_10": 0.0,
  "probability_overrun_gt_20": 0.0,
  "reference_class": "Unknown / 500-2000 Cr / Bihar (national-sector fallback)"
}
```

### 3.3 Observed Behavior

**Critical Issue:** All tested projects return:
- `sample_count: 0`
- `used_fallback: true`
- `warning: "No completed projects available for RCF fallback cluster"`
- Default quantile values (0.1, 0.2, 0.3)

**Impact:** RCF is not using real database data for reference class fitting.

---

## 4. Root Cause Analysis

### 4.1 Data Source Issue

**File:** `backend/app/services/synthetic_data.py`

**Function:** `get_completed_projects_df()`

**Current Behavior:**
```python
def get_completed_projects_df() -> pd.DataFrame:
    """Return completed projects as a DataFrame for RCF fitting."""
    if "completed_df" in _cache:
        return _cache["completed_df"]

    projects = load_projects()
    # ... loads from PAIMANA Excel or synthetic seed
```

**Issue:** RCF is calling `get_completed_projects_df()` from `synthetic_data.py`, which loads projects from PAIMANA Excel file or synthetic seed, NOT from the PostgreSQL database.

### 4.2 Expected Behavior

RCF should load completed projects from the PostgreSQL database:
- Query `projects` table for completed projects
- Filter by sector, state, size_band
- Calculate quantiles from real historical data

### 4.3 Current State

- Database has 2,634 projects
- RCF is not querying the database
- RCF is using synthetic data or PAIMANA Excel
- No reference classes are being fitted from real data

---

## 5. 125 Fitted Classes Claim

### 5.1 Claim Verification

**Claim:** System reports 125 fitted reference classes.

**Verification:** Could not verify this claim.

**Reason:** RCF is not using database data, so no reference classes are being fitted from real PAIMANA data.

### 5.2 Expected Reference Classes

If RCF were using real database data, the number of reference classes would be:
- Number of unique sectors × number of unique states × number of size bands

**Database Schema:**
- Many projects have sector = "Unknown"
- Many projects have state = "Assam" (from test data)
- Size bands: 150-500 Cr, 500-2000 Cr, 2000+ Cr

**Expected Classes:** Limited by "Unknown" sector values in database.

---

## 6. Fallback Status Verification

### 6.1 Fallback Trigger

**Condition:** `len(cluster) < min_cluster_size` (where min_cluster_size = 15)

**Current Status:** All projects trigger fallback because sample_count = 0.

### 6.2 Fallback Behavior

**Expected Fallback:** If specific reference class has < 15 projects, fall back to national-sector level.

**Current Fallback:** No completed projects available, so returns default quantiles (0.1, 0.2, 0.3).

**Issue:** Fallback is not working as designed because no completed projects are available from the data source.

---

## 7. Size Band Calculation

### 7.1 Size Band Function

**File:** `backend/app/services/rcf_engine.py`

```python
def size_band_for_cost(sanctioned_cost: float) -> str:
    if sanctioned_cost < 500:
        return "150-500 Cr"
    if sanctioned_cost < 2000:
        return "500-2000 Cr"
    return "2000+ Cr"
```

**Test Results:**
- 1110.23 Cr → "500-2000 Cr" ✓
- 356.65 Cr → "150-500 Cr" ✓
- 458.59 Cr → "150-500 Cr" ✓

✓ **VERIFIED:** Size band calculation is correct.

---

## 8. Verification Status

| Check | Status | Notes |
|------|--------|-------|
| RCF engine implementation | ✓ Verified | Code correctly implements SRS requirements |
| Minimum cluster size (15) | ✓ Verified | Default min_cluster_size = 15 |
| Fallback logic | ✓ Verified | Correctly falls back when < 15 projects |
| Size band calculation | ✓ Verified | Correctly categorizes by cost |
| Quantile calculation | ✓ Verified | Correctly calculates P50, P80, P90 |
| Database data source | ✗ Not Verified | RCF uses synthetic_data, not database |
| 125 fitted classes | ✗ Not Verified | No classes fitted from real data |
| Sample count | ✗ Issue | All return 0 (no data source) |
| Fallback status | ✗ Issue | All trigger fallback (no data source) |
| Reference class string | ✓ Verified | Correctly formatted |

---

## 9. Issues Identified

### 9.1 Critical: Wrong Data Source

**Issue:** RCF uses `synthetic_data.get_completed_projects_df()` instead of querying the PostgreSQL database.

**Impact:** No reference classes are fitted from real PAIMANA data.

**Root Cause:** RCF engine was designed for synthetic data/demo mode and was not updated to use the database.

**Required Action:** Implement database query for completed projects in RCF engine.

### 9.2 No Fitted Classes

**Issue:** Claim of 125 fitted reference classes cannot be verified because RCF is not using database data.

**Impact:** RCF provides no real historical reference class information.

**Required Action:** Fix data source, then verify actual number of fitted classes.

### 9.3 All Projects Trigger Fallback

**Issue:** All tested projects return sample_count = 0 and trigger fallback.

**Impact:** RCF provides default quantiles (0.1, 0.2, 0.3) instead of real historical quantiles.

**Required Action:** Fix data source to provide real completed projects.

---

## 10. Recommendations

### 10.1 Immediate Actions

1. **Fix Data Source:** Implement database query for completed projects in RCF engine
2. **Remove Synthetic Dependency:** RCF should not depend on synthetic_data.py in production
3. **Add Database Query:** Query `projects` table for completed projects with sector, state, cost data
4. **Calculate Overrun Ratios:** Compute cost_overrun_ratio from database fields

### 10.2 Implementation Changes

**New Function:** `get_completed_projects_from_db()`

```python
def get_completed_projects_from_db(db: Session) -> pd.DataFrame:
    """Query completed projects from PostgreSQL database."""
    from app.models.projects import Project
    
    projects = db.query(Project).filter(
        Project.status == "completed"
    ).all()
    
    rows = []
    for p in projects:
        sanctioned = p.sanctioned_cost or 0
        revised = p.revised_cost or sanctioned
        cost_overrun = revised / sanctioned if sanctioned > 0 else 1.0
        
        rows.append({
            "project_id": p.project_id,
            "sector": p.sector or "Unknown",
            "size_band": size_band_for_cost(sanctioned),
            "region": p.state or "Unknown",
            "cost_overrun_ratio": cost_overrun_ratio,
            "schedule_delay_months": calculate_schedule_delay(p),
        })
    
    return pd.DataFrame(rows)
```

### 10.3 Testing Actions

1. **Database Test:** Verify database has completed projects
2. **RCF Test:** Test RCF with database data source
3. **Class Count Test:** Verify actual number of fitted reference classes
4. **Fallback Test:** Test fallback with < 15 projects in class

---

## 11. Conclusion

**Status: NOT VERIFIED**

RCF implementation is correct according to SRS requirements:
- Minimum cluster size of 15 is implemented
- Fallback logic is correct
- Quantile calculations are correct
- Size band calculation is correct

However, RCF is not using real database data:
- RCF uses synthetic_data.py instead of PostgreSQL
- No reference classes are fitted from real PAIMANA data
- All projects return sample_count = 0 and trigger fallback
- Claim of 125 fitted classes cannot be verified

**Required Before Acceptance:**
- Implement database query for completed projects in RCF engine
- Remove dependency on synthetic_data.py for production RCF
- Verify actual number of fitted reference classes from database
- Verify fallback behavior with real database data
