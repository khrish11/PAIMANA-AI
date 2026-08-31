# Database Import Audit Report

**Date:** August 31, 2026  
**Objective:** Trace PAIMANA PDFs → PostgreSQL field mapping and identify data loss points.

---

## 1. Data Pipeline Overview

```
REAL PAIMANA PDFs
→ extracted CSVs (data/extracted/)
→ normalized CSV (data/processed/all_projects_normalized.csv)
→ PostgreSQL (via backend/import_paimana_data.py)
→ Intelligence Services (RCF, PBE, DCS, Risk, NID, PDR)
```

---

## 2. Source Data Analysis

### 2.1 Extracted CSV Format

**File:** `data/extracted/FlashReport_April2026_page100_table0.csv`

**Header Format:** Complex multi-line header with embedded parentheses

**Fields Available in Extracted CSV:**
- Sl.No
- Project Name
- Agency (embedded in Project Name field)
- Project Code / Legacy OCMS Code / PMGID (embedded in Project Name field)
- State
- Date of Approval / Start Date (MM/YYYY)
- Original/Target DoC (MM/YYYY)
- Revised DoC (MM/YYYY)
- Original Cost (Rs. Crore)
- Revised Cost (Rs. Crore)
- Cumulative Expenditure (Rs. Crore)
- Physical Progress (%)

**Fields NOT Available in Extracted CSV:**
- Sector
- Ministry
- Narrative text

### 2.2 Normalized CSV Fields

**File:** `data/processed/all_projects_normalized.csv`

**Header:** `project_id,project_name,agency,project_code,ministry,sector,state,approval_date,original_completion_date,revised_completion_date,original_cost_crore,revised_cost_crore,cumulative_expenditure_crore,physical_progress_pct,reporting_month,source_file,source_page,extraction_timestamp`

**Fields Present:**
- project_id ✓
- project_name ✓
- agency ✓
- project_code ✓
- ministry ✓
- sector ✓
- state ✓
- approval_date ✓
- original_completion_date ✓
- revised_completion_date ✓
- original_cost_crore ✓
- revised_cost_crore ✓
- cumulative_expenditure_crore ✓
- physical_progress_pct ✓
- reporting_month ✓
- source_file ✓
- source_page ✓
- extraction_timestamp ✓

**Fields Missing:**
- narrative ✗ (not in normalized CSV)

### 2.3 Data Dictionary Statistics

**File:** `data/processed/data_dictionary.csv`

| Field | Missing Count | Missing Rate | Unique Count | Sample Values |
|-------|--------------|-------------|-------------|---------------|
| agency | 1,462 | 6.45% | 3,434 | NHIDCL N24002025) (-, NHIDCL N24001419) (- |
| approval_date | 1,491 | 6.58% | 266 | 01/2023, 03/2023, 12/2023 |
| cumulative_expenditure_crore | 946 | 4.17% | 11,609 | 0.0, 217.2, 569.61 |
| ministry | 17,452 | 77.01% | 36 | PROJECT ID, Department of Telecommunications |
| original_completion_date | 1,486 | 6.56% | 202 | 12/2026, 05/2025, 08/2025 |
| original_cost_crore | 2 | 0.01% | 2,845 | 356.65, 458.59, 890.33 |
| physical_progress_pct | 2,457 | 10.84% | 2,971 | 20.45, 83.39, 81.9 |
| project_code | 1,721 | 7.59% | 2,241 | 618339, 618340, 618351 |
| project_id | 0 | 0.00% | 2,636 | PC-618339, PC-618340, PC-618351 |
| project_name | 5 | 0.02% | 2,894 | Widening/Improvement to 2-Lane Lane with Paved Shoulder |
| reporting_month | 0 | 0.00% | 13 | 2026-04, 2025-08, 2025-12 |
| revised_completion_date | 8,088 | 35.69% | 158 | 07/2026, 06/2026, 11/2026 |
| revised_cost_crore | 1,423 | 6.28% | 2,517 | 356.65, 458.59, 693.15 |
| **sector** | **19,051** | **84.07%** | 32 | Telecommunication, Waste & Water, Water Resources |
| source_file | 0 | 0.00% | 1,311 | FlashReport_April2026_page100_table0.csv |
| source_page | 0 | 0.00% | 157 | 100, 101, 102 |
| state | 7 | 0.03% | 256 | Assam, Bihar, Chhattisgarh |

**Critical Issue:** 84.07% of records have missing sector data.

---

## 3. Import Script Analysis

### 3.1 Import Script Location

**File:** `backend/import_paimana_data.py`

### 3.2 Field Mapping in Import Script

**Sector Mapping (Lines 76-79):**
```python
sector = str(row.get('sector', 'Unknown'))
if sector == 'nan' or sector == '':
    sector = 'Unknown'
sector = sector[:120]
```

**Issue:** If sector is missing in normalized CSV, it defaults to 'Unknown'. Since 84.07% of normalized records have missing sector, most projects become 'Unknown'.

**Ministry Mapping (Lines 81-84):**
```python
ministry = str(row.get('ministry', 'Unknown'))
if ministry == 'nan' or ministry == '' or ministry == 'PROJECT ID':
    ministry = 'Unknown'
ministry = ministry[:160]
```

**Issue:** If ministry is missing in normalized CSV, it defaults to 'Unknown'. Since 77.01% of normalized records have missing ministry, most projects become 'Unknown'.

**State Mapping (Lines 86-89):**
```python
state = str(row.get('state', 'Unknown'))
if state == 'nan' or state == '' or len(state) > 120:
    state = 'Unknown'
state = state[:120]
```

**Status:** State has only 0.03% missing rate, so this mapping works well.

**Cost Mapping (Lines 91-95):**
```python
sanctioned_cost = float(row.get('original_cost_crore', 0))
if pd.isna(sanctioned_cost) or sanctioned_cost <= 0:
    # Skip projects with invalid or zero cost
    skipped += 1
    continue
```

**Issue:** Projects with zero or invalid cost are skipped entirely.

**Narrative Text Mapping (Lines 183, 197):**
```python
existing.narrative_text = str(row.get('narrative', '')) if pd.notna(row.get('narrative')) and row.get('narrative') != '' else None
```

**Issue:** The import script looks for a 'narrative' field in the normalized CSV, but this field does not exist in the normalized CSV schema.

---

## 4. Field Mapping Table

| Source Field (Extracted CSV) | Normalized Field | Database Column | Mapping Status |
|------------------------------|------------------|-----------------|---------------|
| Agency (embedded in Project Name) | agency | projects.agency | ✓ Mapped |
| Project Code (embedded in Project Name) | project_code | projects.project_code | ✓ Mapped |
| State | state | projects.state | ✓ Mapped |
| Date of Approval | approval_date | projects.approved_date | ✓ Mapped |
| Original/Target DoC | original_completion_date | N/A | ✓ Mapped (not in DB) |
| Revised DoC | revised_completion_date | cuf_submissions.planned_completion | ✓ Mapped |
| Original Cost | original_cost_crore | projects.sanctioned_cost | ✓ Mapped |
| Revised Cost | revised_cost_crore | cuf_submissions.revised_cost | ✓ Mapped |
| Cumulative Expenditure | cumulative_expenditure_crore | cuf_submissions.expenditure | ✓ Mapped |
| Physical Progress (%) | physical_progress_pct | cuf_submissions.physical_progress | ✓ Mapped |
| **Sector** | **sector** | **projects.sector** | ✗ **84% missing** |
| **Ministry** | **ministry** | **projects.ministry** | ✗ **77% missing** |
| **Narrative** | **narrative** | **cuf_submissions.narrative_text** | ✗ **Not in source** |

---

## 5. Root Cause Analysis

### 5.1 Sector Missing (84.07%)

**Root Cause:** Sector information is NOT present in the project-level extracted CSV files from PAIMANA PDFs.

**Evidence:**
- Extracted CSV header (table0) does not include a sector field
- Normalized CSV has sector field with 84.07% missing rate
- Import script defaults missing sector to 'Unknown'

**NEW FINDING:** Sector information exists in summary tables (table1) that map ministries to sectors.

**Evidence:**
- File: `FlashReport_April2026_page24_table1.csv`
- Structure: Allocated To (Ministry) | Sector | Project Count | Original Cost | Cumulative Expenditure
- Sample mappings:
  - Ministry of Road Transport & Highways → Roads & Highways
  - Ministry of Railways → Railways
  - Ministry of Power → Coal, Electricity Generation, Transmission & Distribution
  - Ministry of Petroleum & Natural Gas → Energy Storage, Oil & Gas
  - Department of Telecommunications → Telecommunication
  - Ministry of Housing & Urban Affairs → Construction, Real Estate, Urban Public Transport, Waste & Water

**Impact:**
- PBE cohort filtering by sector is ineffective
- RCF reference classes by sector are degraded
- Network sector nodes are mostly 'Unknown'

**Solution:** Create a ministry-to-sector mapping table from the summary tables and use it to populate sector for projects.

### 5.2 Ministry Missing (77.01%)

**Root Cause:** Ministry information is NOT present in the project-level extracted CSV files from PAIMANA PDFs.

**Evidence:**
- Extracted CSV header (table0) does not include a ministry field
- Normalized CSV has ministry field with 77.01% missing rate
- Import script defaults missing ministry to 'Unknown'

**NEW FINDING:** Ministry information exists in summary tables (table1) that map agencies to ministries.

**Evidence:**
- File: `FlashReport_April2026_page24_table1.csv`
- Structure: Allocated To (Ministry) | Sector | Project Count | Original Cost | Cumulative Expenditure
- Sample ministries found:
  - Department for Promotion of Industry & Internal Trade
  - Department of Higher Education
  - Department of Sports
  - Department of Telecommunications
  - Department of Water Resources, River Development & GR
  - Ministry of Civil Aviation
  - Ministry of Coal
  - Ministry of Health & Family Welfare
  - Ministry of Housing & Urban Affairs
  - Ministry of Labour and Employment
  - Ministry of Mines
  - Ministry of Petroleum & Natural Gas
  - Ministry of Ports, Shipping and Waterways
  - Ministry of Power
  - Ministry of Railways
  - Ministry of Road Transport & Highways
  - Ministry of Steel

**Impact:**
- Ministry-based filtering is ineffective
- Governance by ministry is degraded

**Solution:** Create an agency-to-ministry mapping table from the summary tables and use it to populate ministry for projects.

### 5.3 Narrative Text Missing (100%)

**Root Cause:** Narrative text field does not exist in the extracted CSV files from PAIMANA PDFs.

**Evidence:**
- Searched 100 extracted CSV files for fields containing: narrative, remark, observation, reason
- Found 0 files with any of these fields
- Normalized CSV schema does not include a 'narrative' field
- Import script looks for 'narrative' field but it doesn't exist
- Database has 0 narrative_text records out of 19,793 submissions

**Conclusion:** PAIMANA Flash Reports do not contain narrative text fields. The reports are structured as tabular data with cost, schedule, and progress metrics, but do not include free-text narrative descriptions.

**Impact:**
- NID (Narrative Intelligence Detection) is unavailable
- PDR (Positive Deviance Radar) cannot extract insights from narratives

**Solution:** Document that NID and PDR narrative-based features are unavailable due to lack of narrative data in PAIMANA source documents. These features would require alternative data sources or manual narrative collection.

### 5.4 Agency Parsing Issues

**Root Cause:** Agency is embedded in the Project Name field with parentheses.

**Evidence:**
- Extracted CSV: `(NHIDCL)` embedded in Project Name
- Normalized CSV: agency field contains `NHIDCL N24002025) (-` with extra characters

**Impact:**
- Agency names are not clean
- Agency-based filtering may be inaccurate

---

## 6. Recommendations

### 6.1 Immediate Actions

1. **Audit PAIMANA PDFs:** Check if sector and ministry information exists in the original PDFs in a different section/table
2. **Check Alternative Tables:** Look for summary tables or index tables in PAIMANA reports that might contain sector/ministry mappings
3. **Extract Agency Cleanly:** Improve agency extraction to remove extra characters and codes
4. **Narrative Investigation:** Search for narrative/remarks/observations fields in other extracted tables

### 6.2 Data Quality Improvements

1. **Sector Mapping:** If sector exists in PDFs, extract it. If not, map from agency or project type.
2. **Ministry Mapping:** If ministry exists in PDFs, extract it. If not, map from agency.
3. **Narrative Extraction:** Search for remarks, observations, issues, delay reasons fields in PDFs.
4. **Agency Normalization:** Clean agency names by removing codes and extra characters.

### 6.3 Fallback Strategies

1. **Sector from Agency:** Create a mapping table from agency to sector based on known agency classifications.
2. **Ministry from Agency:** Create a mapping table from agency to ministry based on known agency classifications.
3. **Narrative Unavailable:** Document that NID and PDR are unavailable due to lack of narrative data in source.

---

## 7. Next Steps

1. **Review PAIMANA PDFs:** Manually inspect PAIMANA PDFs to identify if sector/ministry/narrative information exists
2. **Extract Alternative Tables:** Check if there are summary tables or index tables with sector/ministry information
3. **Create Mapping Tables:** If sector/ministry cannot be extracted directly, create mapping tables from agency
4. **Update Import Script:** Modify import script to use mapping tables or improved extraction logic
5. **Re-import Data:** Re-run import script with improved mappings
6. **Verify Database:** Verify database has improved sector/ministry coverage
