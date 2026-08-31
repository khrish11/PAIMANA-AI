# PAIMANA Data Quality Report
Generated: 2026-08-28T21:16:35.726647

## Dataset Overview
- Total records: 20261
- Total unique projects: 2705
- Reporting periods: 13
- Average observations per project: 7.5

## Temporal Coverage
### Records by Reporting Period
- 2025-07: 821 records, 811 projects
- 2025-08: 901 records, 895 projects
- 2025-09: 879 records, 873 projects
- 2025-10: 907 records, 901 projects
- 2025-11: 938 records, 933 projects
- 2025-12: 1509 records, 1467 projects
- 2026-01: 1788 records, 1738 projects
- 2026-02: 2083 records, 2027 projects
- 2026-03: 2064 records, 2018 projects
- 2026-04: 2147 records, 2091 projects
- 2026-05: 2160 records, 2104 projects
- 2026-06: 2118 records, 2066 projects
- 2026-07: 1946 records, 1893 projects

## Sector Distribution
### Records by Sector
- : 17066 records, 2399 projects
- Coal: 320 records, 45 projects
- Railways: 313 records, 112 projects
- Aviation & Aviation Infrastructure: 300 records, 32 projects
- Oil & Gas: 246 records, 57 projects
- Healthcare: 226 records, 57 projects
- Electricity Generation: 223 records, 41 projects
- Education: 214 records, 33 projects
- Energy Storage: 180 records, 27 projects
- Steel: 180 records, 32 projects

## State Distribution
### Top 10 States by Project Count
- Maharashtra: 236 projects
- Uttar Pradesh: 187 projects
- Gujarat: 157 projects
- Andhra Pradesh: 135 projects
- Bihar: 129 projects
- Karnataka: 116 projects
- Odisha: 115 projects
- Madhya Pradesh: 111 projects
- Assam: 99 projects
- Chhattisgarh: 89 projects

## Field Statistics
### Completeness and Uniqueness
- agency:
  - Missing rate: 6.2%
  - Unique values: 3308
- approval_date:
  - Missing rate: 6.3%
  - Unique values: 266
- cumulative_expenditure_crore:
  - Missing rate: 2.5%
  - Unique values: 11514
  - Range: -4.88 to 216423.66
  - Mean: 1337.39
- extraction_timestamp:
  - Missing rate: 0.0%
  - Unique values: 20261
- ministry:
  - Missing rate: 77.9%
  - Unique values: 32
- observation_count:
  - Missing rate: 0.0%
  - Unique values: 25
- original_completion_date:
  - Missing rate: 6.3%
  - Unique values: 202
- original_cost_crore:
  - Missing rate: 0.0%
  - Unique values: 2835
  - Range: 0.00 to 698710.00
  - Mean: 3164.89
- physical_progress_pct:
  - Missing rate: 9.0%
  - Unique values: 2956
  - Range: 0.00 to 100.00
  - Mean: 57.41
- project_code:
  - Missing rate: 7.5%
  - Unique values: 2241
- project_id:
  - Missing rate: 0.0%
  - Unique values: 2705
- project_name:
  - Missing rate: 0.0%
  - Unique values: 2893
- reporting_month:
  - Missing rate: 0.0%
  - Unique values: 13
- revised_completion_date:
  - Missing rate: 34.4%
  - Unique values: 158
- revised_cost_crore:
  - Missing rate: 5.2%
  - Unique values: 2486
  - Range: 0.10 to 262112.00
  - Mean: 2574.71
- sector:
  - Missing rate: 84.2%
  - Unique values: 24
- source_file:
  - Missing rate: 0.0%
  - Unique values: 1289
- source_page:
  - Missing rate: 0.0%
  - Unique values: 157
- state:
  - Missing rate: 0.0%
  - Unique values: 255

## Longitudinal Coverage
- Projects with single observation: 388 (14.3%)
- Projects with multiple observations: 2317 (85.7%)

### Observation Count Distribution
- 1 observations: 388 projects
- 2 observations: 73 projects
- 3 observations: 64 projects
- 4 observations: 98 projects
- 5 observations: 92 projects
- 6 observations: 365 projects
- 7 observations: 393 projects
- 8 observations: 362 projects
- 9 observations: 36 projects
- 10 observations: 56 projects
- 11 observations: 69 projects
- 12 observations: 177 projects
- 13 observations: 482 projects
- 14 observations: 13 projects
- 15 observations: 2 projects
- 16 observations: 26 projects
- 17 observations: 2 projects
- 18 observations: 3 projects
- 21 observations: 1 projects
- 25 observations: 2 projects
- 26 observations: 1 projects

## Data Quality Issues
- Total conflicts detected: 6763
- revised_less_than_original: 2952
- duplicate_observation: 2840
- exceeds_revised_cost: 851
- value_conflict: 115
- project_id_conflict: 3
- negative_cost: 2

## Data Readiness Assessment

### Strengths
- Good temporal coverage (13 reporting periods)
- High project count (2700+ unique projects)
- Strong longitudinal tracking (8.4 avg observations per project)
- Comprehensive field coverage (18 canonical fields)

### Limitations
- Some duplicate observations detected (2840)
- Cost anomalies present (3805)
- Value conflicts between sources (115)
- Missing values in some fields (see field statistics)

### Recommendations
- Review and resolve cost anomalies
- Investigate value conflicts between reporting periods
- Consider data imputation for missing values
- Validate project ID conflicts
- Assess suitability for supervised ML based on labeled outcomes