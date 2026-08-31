# PDR Verification Report

**Date:** August 30, 2026  
**Objective:** Verify PDR (Positive Deviance Radar) real pipeline with no forced positive deviants.

---

## 1. PDR Purpose and Design

### 1.1 PDR Definition

PDR (Positive Deviance Radar) identifies projects that perform significantly better than their reference class peers (positive deviants) and extracts actionable insights (playbooks) from their narratives.

### 1.2 Positive Deviance Detection

**Criteria:**
- Hard reference class (sector, state, size band)
- DCS threshold (minimum data confidence)
- Minimum history (months active)
- Deviance threshold (z-score for cost/schedule residuals)

**No Forced Deviants:** If no projects satisfy the criteria, return an honest empty state. Do not force a positive deviant.

### 1.3 Playbook Generation

**Requirements:**
- >= 3 independent source projects
- Extracted actions from narrative text
- Clustered by category
- Confidence tier based on source count and specificity

**No Fabricated Playbooks:** If there are no real playbooks, return "No evidence-backed playbooks currently available."

---

## 2. PDR API Endpoints

### 2.1 Available Endpoints

**File:** `backend/app/api/v1/positive_deviance.py`

**Endpoints:**
- `GET /api/v1/positive-deviants` - List positive deviants
- `GET /api/v1/playbooks` - List available playbooks
- `GET /api/v1/playbooks/{playbook_id}` - Get playbook details
- `GET /api/v1/projects/{project_id}/suggested-playbooks` - Get suggested playbooks for a project
- `POST /api/v1/projects/{project_id}/suggested-playbooks/{suggestion_id}/dismiss` - Dismiss suggestion
- `POST /api/v1/projects/{project_id}/suggested-playbooks/{suggestion_id}/viewed` - Mark as viewed

### 2.2 Missing Endpoint

**Expected but Not Found:**
- `GET /api/v1/projects/{project_id}/pdr` - Project-level PDR endpoint

**Test Result:** Returns 404 Not Found

**Impact:** PDR is not available at the project level, only as a global listing.

---

## 3. Real PDR Pipeline Tests

### 3.1 Positive Deviants Endpoint

**Request:**
```
GET /api/v1/positive-deviants
```

**Response:**
```json
{
  "positive_deviants": [],
  "total_count": 0,
  "metadata": {
    "total_count": 0,
    "sectors": 0,
    "states": 0
  }
}
```

**Result:** No positive deviants detected in database.

### 3.2 Playbooks Endpoint

**Request:**
```
GET /api/v1/playbooks
```

**Response:**
```json
{
  "playbooks": [],
  "total_count": 0,
  "filters_applied": {}
}
```

**Result:** No playbooks available in database.

### 3.3 Suggested Playbooks Endpoint

**Request:**
```
GET /api/v1/projects/{project_id}/suggested-playbooks
```

**Expected:** List of playbook suggestions for the project

**Result:** Not tested (no playbooks exist to suggest)

---

## 4. Database State

### 4.1 Positive Deviants Table

**Query:** `SELECT COUNT(*) FROM positive_deviants`

**Expected:** Count of detected positive deviants

**Actual:** 0 positive deviants in database

### 4.2 Playbooks Table

**Query:** `SELECT COUNT(*) FROM playbooks`

**Expected:** Count of generated playbooks

**Actual:** 0 playbooks in database

### 4.3 Extracted Actions Table

**Query:** `SELECT COUNT(*) FROM extracted_actions`

**Expected:** Count of extracted actions from narratives

**Actual:** 0 extracted actions in database (consistent with 0% narrative coverage)

---

## 5. PDR Detection Logic

### 5.1 Detection Service

**File:** `backend/app/services/positive_deviance.py`

**Function:** `batch_detect()`

**Criteria:**
- Hard reference class filtering
- DCS threshold check
- Minimum history check
- Z-score calculation for cost/schedule residuals

### 5.2 Fallback Behavior

**Code:**
```python
if not result:
    detector = PositiveDevianceDetector()
    fallback = detector.batch_detect(limit=limit, offset=offset, sector=sector, state=state)
```

**Behavior:** If database has no positive deviants, falls back to synthetic data detection.

**Issue:** Fallback to synthetic data may return fabricated positive deviants, which violates the requirement to not force positive deviants.

---

## 6. Playbook Generation Logic

### 6.1 Playbook Clusterer

**File:** `backend/app/services/playbook_clustering.py`

**Function:** `cluster_actions_into_playbooks()`

**Requirements:**
- >= 3 independent source projects
- Extracted actions from narrative text
- Clustered by category
- Confidence tier based on source count

### 6.2 Real Data Status

**Narrative Coverage:** 0% (0/19,793 submissions)

**Extracted Actions:** 0

**Source Projects:** 0

**Result:** No playbooks can be generated from real data because no narrative text exists.

---

## 7. Verification of Requirements

### 7.1 No Forced Positive Deviants

**Requirement:** If no projects satisfy criteria, return honest empty state.

**Current Behavior:**
- Database returns 0 positive deviants ✓
- API returns empty list ✓
- Fallback to synthetic data may return fabricated deviants ✗

**Issue:** Fallback to synthetic data detection may return fabricated positive deviants.

**Required Action:** Disable fallback to synthetic data for PDR detection in production.

### 7.2 No Fabricated Playbooks

**Requirement:** If no real playbooks, return "No evidence-backed playbacks currently available."

**Current Behavior:**
- Database returns 0 playbooks ✓
- API returns empty list ✓
- No fabricated playbooks returned ✓

**Status:** ✓ VERIFIED - No fabricated playbooks are returned.

### 7.3 Minimum Source Projects

**Requirement:** Playbooks require >= 3 independent source projects.

**Current Behavior:**
- 0 source projects available (no narrative text)
- No playbooks generated ✓

**Status:** ✓ VERIFIED - Playbooks are not generated without sufficient source projects.

---

## 8. Issues Identified

### 8.1 Project-Level PDR Endpoint Missing

**Issue:** `GET /api/v1/projects/{project_id}/pdr` endpoint does not exist

**Impact:** PDR is not available at the project level for individual project analysis

**Required Action:** Implement project-level PDR endpoint or document that PDR is only available as a global listing.

### 8.2 Synthetic Fallback for Positive Deviants

**Issue:** When database has no positive deviants, API falls back to synthetic data detection

**Impact:** May return fabricated positive deviants, violating the requirement to not force positive deviants

**Required Action:** Disable fallback to synthetic data for PDR detection in production.

### 8.3 No Narrative Text

**Issue:** 0% narrative coverage prevents any real PDR detection or playbook generation

**Impact:** PDR cannot run on real data

**Root Cause:** PDF import pipeline not extracting narrative text

**Required Action:** Fix PDF import pipeline to extract narrative text.

---

## 9. Verification Status

| Check | Status | Notes |
|------|--------|-------|
| Positive deviants endpoint | ✓ Exists | Returns empty list (0 deviants) |
| Playbooks endpoint | ✓ Exists | Returns empty list (0 playbooks) |
| Project-level PDR endpoint | ✗ Missing | Returns 404 |
| No forced positive deviants | ⚠️ Partial | Database returns empty, but synthetic fallback may fabricate |
| No fabricated playbooks | ✓ Verified | Returns empty list, no fabricated playbooks |
| Minimum source projects (>=3) | ✓ Verified | No playbooks generated without sufficient sources |
| Real data execution | ✗ Blocked | 0% narrative coverage prevents real PDR |

---

## 10. Recommendations

### 10.1 Immediate Actions

1. **Disable Synthetic Fallback:** Remove fallback to synthetic data for PDR detection in production
2. **Implement Project-Level Endpoint:** Add `GET /api/v1/projects/{project_id}/pdr` endpoint for individual project analysis
3. **Add Empty State Message:** Return clear message "No evidence-backed playbooks currently available" when playbooks list is empty

### 10.2 Data Quality Actions

1. **Fix Narrative Import:** Implement narrative text extraction from PDF reports
2. **Populate Narrative Field:** Ensure narrative text is stored in cuf_submissions.narrative_text
3. **Enable PDR Detection:** Once narrative text is available, run PDR detection pipeline

### 10.3 Testing Actions

1. **Test Empty State:** Verify PDR returns honest empty state when no positive deviants exist
2. **Test Playbook Generation:** Test playbook generation once narrative text is available
3. **Test Minimum Sources:** Verify playbooks are not generated with < 3 source projects

---

## 11. Conclusion

**Status: NOT EXECUTABLE**

PDR implementation exists but cannot execute on real data:
- Positive deviants endpoint exists and returns empty list (no forced deviants from database)
- Playbooks endpoint exists and returns empty list (no fabricated playbooks)
- Project-level PDR endpoint is missing (404)
- Synthetic fallback may fabricate positive deviants (violates requirement)
- 0% narrative coverage prevents any real PDR detection or playbook generation

**Required Before Real-Data Execution:**
- Disable synthetic fallback for PDR detection
- Implement project-level PDR endpoint
- Fix PDF import pipeline to extract narrative text
- Run PDR detection pipeline once narrative text is available
