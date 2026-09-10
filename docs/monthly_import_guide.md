# PAIMANA Monthly Import Guide

This guide provides detailed instructions for performing monthly bulk imports of CUF data into PAIMANA.

---

## Overview

Monthly imports are the primary method for updating project progress data across many projects simultaneously. This guide covers:

- CSV preparation and formatting
- Import workflow steps
- Validation and preview
- Handling duplicates and revisions
- Post-import verification
- Troubleshooting common issues

---

## Prerequisites

### Before Import
- Access to PAIMANA frontend interface
- Valid CSV file with monthly CUF data
- Appropriate user permissions (AGENCY or ADMIN role)
- Projects must exist in system (for CUF submissions)
- Understanding of data validation rules

### Data Requirements
- Project codes must match existing projects
- Reporting months must be in YYYY-MM format
- Physical progress must be 0-100
- Expenditure must be non-negative
- Dates must be in YYYY-MM-DD format

---

## CSV Preparation

### File Format
- **File Type**: CSV (Comma Separated Values)
- **Encoding**: UTF-8
- **Delimiter**: Comma (,)
- **Line Ending**: Unix (LF) or Windows (CRLF)

### Column Headers

#### For New Projects (if including in import)
```
project_code,project_name,ministry,sector,state,implementing_agency,department,sanctioned_cost,approved_date,original_completion_date
```

#### For Monthly CUF Submissions
```
project_code,reporting_month,revised_cost,expenditure,physical_progress,planned_completion,narrative_text
```

### Data Types and Formats

| Column | Type | Format | Required | Example |
|--------|------|--------|----------|---------|
| project_code | String | P-YYYY-NNN | Yes | P-2026-001 |
| project_name | String | Text | Yes | NH-48 Expansion |
| ministry | String | Text | Yes | Ministry of Road Transport |
| sector | String | Text | Yes | Roads |
| state | String | Text | Yes | Maharashtra |
| implementing_agency | String | Text | Yes | NHAI |
| department | String | Text | No | Transport |
| sanctioned_cost | Number | Decimal | Yes | 1000.50 |
| approved_date | Date | YYYY-MM-DD | Yes | 2025-01-15 |
| original_completion_date | Date | YYYY-MM-DD | Yes | 2027-12-31 |
| reporting_month | Date | YYYY-MM | Yes | 2026-08 |
| revised_cost | Number | Decimal | No | 1050.00 |
| expenditure | Number | Decimal | No | 500.00 |
| physical_progress | Number | Decimal | Yes | 45.5 |
| planned_completion | Date | YYYY-MM-DD | No | 2028-03-31 |
| narrative_text | String | Text | No | Progress on track |

### Sample CSV Files

#### Example 1: New Projects Only
```csv
project_code,project_name,ministry,sector,state,implementing_agency,department,sanctioned_cost,approved_date,original_completion_date
P-2026-001,NH-48 Expansion,Ministry of Road Transport,Roads,Maharashtra,NHAI,Transport,1000.00,2025-01-15,2027-12-31
P-2026-002,Railway Electrification,Ministry of Railways,Railways,Karnataka,SWR,Transport,500.00,2025-03-01,2026-12-31
P-2026-003,Power Grid Upgrade,Ministry of Power,Power,Tamil Nadu,TANGEDCO,Power,750.00,2025-02-20,2028-06-30
```

#### Example 2: Monthly CUF Submissions Only
```csv
project_code,reporting_month,revised_cost,expenditure,physical_progress,planned_completion,narrative_text
P-2026-001,2026-08,1050.00,500.00,45.5,2028-03-31,Progress on track with minor delays
P-2026-002,2026-08,,300.00,60.0,,Ahead of schedule
P-2026-003,2026-08,780.00,350.00,50.0,2028-06-30,On schedule
```

#### Example 3: Mixed (New Projects + CUF)
```csv
project_code,project_name,ministry,sector,state,implementing_agency,department,sanctioned_cost,approved_date,original_completion_date,reporting_month,revised_cost,expenditure,physical_progress,planned_completion,narrative_text
P-2026-004,Water Supply Project,Ministry of Water Resources,Water,Gujarat,GMWSS,Water,300.00,2025-04-10,2027-03-31,2026-08,,150.00,50.0,2027-03-31,Groundwork completed
```

### CSV Preparation Best Practices

1. **Header Row**
   - Include header row as first line
   - Match column names exactly
   - No extra spaces in column names
   - Use underscores for multi-word names

2. **Data Consistency**
   - Use consistent date formats
   - Ensure project codes are unique
   - Verify numeric values are valid
   - Remove special characters from text fields

3. **File Organization**
   - Use descriptive filenames
   - Include month/year in filename
   - Example: `cuf_import_2026_08.csv`

4. **Validation Before Import**
   - Check for empty required fields
   - Verify project codes exist (for CUF)
   - Check date ranges are realistic
   - Validate numeric ranges

---

## Import Workflow

### Step 1: Access Bulk Import Interface

1. Navigate to `/data-import`
2. Or access from Data Management → "Import CSV/XLSX"

### Step 2: Upload CSV File

1. Click "Select CSV File" button
2. Choose prepared CSV file from local system
3. System automatically reads file content
4. Selected filename displayed

**Supported Formats**: CSV only (XLSX support may be added later)

### Step 3: Validate and Preview

1. Click "STEP 2: Validate & Preview"
2. System parses and validates CSV
3. Preview displays summary statistics:

#### Summary Statistics
- **Rows Detected**: Total rows in CSV
- **New Projects**: Projects being created
- **New Submissions**: New CUF submissions
- **Existing Projects**: Projects already in system
- **Duplicate Submissions**: Months already submitted
- **Revisions**: Potential revisions (if allowed)
- **Invalid Rows**: Rows with validation errors
- **Missing Fields**: Rows with missing required data

#### Validation Errors Table
- Shows specific validation errors
- Includes row number and error message
- Examples:
  - "Row 3: Missing required field: project_code"
  - "Row 7: physical_progress must be between 0 and 100"
  - "Row 12: Invalid date format for approved_date"

#### Preview Rows Table
- Shows first 10 rows of data
- Displays all columns and values
- Use to verify data correctness
- Check for formatting issues

### Step 4: Review and Handle Duplicates

#### If No Duplicates
- Proceed directly to Step 5

#### If Duplicates Detected
- Duplicate submissions count shown
- Two options available:

**Option A: Allow Revisions**
- Check "Allow revisions" checkbox
- Revisions will be created for duplicates
- Revision reason: "Bulk import revision"
- Original versions preserved
- New versions marked as latest

**Option B: Skip Duplicates**
- Leave checkbox unchecked
- Duplicate rows will be skipped
- Only new submissions imported
- No changes to existing data

**Recommendation**: 
- For corrections: Allow revisions
- For new data only: Skip duplicates

### Step 5: Confirm Import

1. Review all preview information
2. Ensure validation errors are acceptable
3. Verify duplicate handling choice
4. Click "STEP 4: Confirm Import"
5. **This is the point of no return**

### Step 6: Import Execution

#### Transaction Process
1. Transaction begins
2. New projects created
3. New submissions created
4. Revisions created (if allowed)
5. Invalid rows skipped
6. Transaction commits on success
7. Transaction rolls back on failure

#### Execution Time
- Depends on number of rows
- Typically 1-5 seconds per 100 rows
- Large imports may take longer
- Status shown during execution

### Step 7: Verify Results

#### Success Message Displays
- **Batch ID**: Unique identifier for this import
- **Status**: completed or failed
- **Rows Detected**: Total rows processed
- **New Projects**: Count of projects created
- **Existing Projects**: Count of existing projects
- **New Submissions**: Count of new submissions
- **Duplicate Submissions**: Count of duplicates
- **Revisions**: Count of revisions made
- **Invalid Rows**: Count of skipped rows
- **Started At**: Import start timestamp
- **Completed At**: Import completion timestamp
- **Error Message**: Details if failed

#### Post-Import Verification
1. Navigate to Data Management
2. Verify new projects appear in list
3. Check project counts updated
4. Navigate to Import History
5. View batch details
6. Verify statistics match expectations

---

## Import History

### Viewing Import History

1. Navigate to `/data-import/history`
2. Or click "View Import History" after import

### Filter Options
- **All**: Show all imports
- **Completed**: Successful imports only
- **Failed**: Failed imports only
- **In Progress**: Currently running imports

### Batch Details
Each batch shows:
- Batch ID (truncated for display)
- Batch Name (filename)
- Status (completed/failed/in_progress)
- Rows Processed
- New Projects
- New Submissions
- Revisions
- Invalid Rows
- Created By
- Completed At

### Audit Trail
- All imports logged in audit table
- Includes user, timestamp, operation details
- Persists across backend restarts
- Complete compliance trail

---

## Idempotency and Re-imports

### Idempotent Behavior
- Uploading the same CSV twice creates no duplicate records
- Second import shows:
  - New: 0
  - Already Existing: N
  - Revised: 0
  - Invalid: 0

### When to Re-import
- Correcting data errors in CSV
- Adding missing rows
- Updating with new data
- Testing import process

### Re-import Procedure
1. Fix CSV file
2. Upload corrected file
3. Preview shows existing rows as "Already Existing"
4. New rows imported
5. Existing rows skipped (unless revisions allowed)

---

## Transaction Safety

### All-or-Nothing Import
- Transaction begins before any writes
- All rows processed in single transaction
- Transaction commits only if all rows succeed
- Transaction rolls back on any failure

### Rollback Scenarios
- Validation error on any row
- Database constraint violation
- System error during import
- Network interruption

### No Partial Imports
- Either all valid rows import, or none
- No partial data in system
- Clear error messages on failure
- Safe to re-import after fixing errors

---

## Error Handling

### Common Import Errors

#### Error: Invalid CSV Format
**Cause**: CSV headers or format incorrect
**Solution**: 
- Verify column names match exactly
- Check delimiter is comma
- Ensure proper encoding (UTF-8)

#### Error: Missing Required Fields
**Cause**: Required columns missing or empty
**Solution**:
- Add missing columns to CSV
- Fill empty required fields
- Check for extra spaces

#### Error: Project Code Not Found
**Cause**: Project doesn't exist for CUF submission
**Solution**:
- Create project first
- Include project in CSV
- Verify project code spelling

#### Error: Invalid Date Format
**Cause**: Date not in YYYY-MM-DD format
**Solution**:
- Convert dates to correct format
- Use Excel or text editor to fix
- Ensure dates are valid calendar dates

#### Error: Physical Progress Out of Range
**Cause**: Value not between 0 and 100
**Solution**:
- Verify progress percentage
- Correct data entry errors
- Ensure values are numeric

#### Error: Negative Expenditure
**Cause**: Expenditure value is negative
**Solution**:
- Verify expenditure figures
- Remove negative signs
- Check data source for errors

#### Error: Transaction Failed
**Cause**: Import error during transaction
**Solution**:
- Review error message for details
- Fix identified issues
- Re-import corrected file
- Transaction rolled back, no data loss

### Error Resolution Workflow

1. **Review Error Message**
   - Note specific error details
   - Identify affected rows
   - Understand error type

2. **Fix CSV File**
   - Correct identified issues
   - Validate all data
   - Save corrected file

3. **Re-import**
   - Upload corrected file
   - Preview to verify fixes
   - Confirm import

4. **Verify Results**
   - Check import status
   - Review batch details
   - Verify data in system

---

## Post-Import Verification

### Dashboard Verification
1. Navigate to `/data-management`
2. Check project counts updated
3. Verify new projects appear
4. Check submission counts

### Project Detail Verification
1. Select a newly imported project
2. Verify project information correct
3. Check latest CUF submission
4. Verify data refresh status

### Import History Verification
1. Navigate to `/data-import/history`
2. Find latest import batch
3. Verify statistics match expectations
4. Check status is "completed"

### Data Quality Verification
1. Navigate to `/data-health`
2. Check quality metrics updated
3. Verify no new validation errors
4. Monitor data coverage

---

## Monthly Import Schedule

### Recommended Schedule
- **Day 1-5**: Collect CUF data from agencies
- **Day 6-7**: Prepare and validate CSV files
- **Day 8**: Perform bulk import
- **Day 9**: Verify import results
- **Day 10**: Review and address issues

### Before Month Close Checklist
- [ ] All CUF data received
- [ ] CSV files prepared
- [ ] Data validated
- [ ] Import performed
- [ ] Results verified
- [ ] Issues addressed
- [ ] Dashboard reviewed
- [ ] Reports generated

---

## Best Practices

### CSV Preparation
- Use consistent formatting
- Validate data before import
- Use descriptive filenames
- Include month/year in filename
- Keep backup of original files

### Import Process
- Review preview carefully
- Handle duplicates appropriately
- Verify results after import
- Check audit log for issues
- Document any corrections

### Data Quality
- Monitor validation errors
- Track import success rate
- Review data quality metrics
- Address issues promptly
- Maintain data standards

### Documentation
- Keep import records
- Document any corrections
- Track revision reasons
- Maintain audit trail
- Review monthly statistics

---

## Troubleshooting Guide

### Import Fails Immediately
**Check**: CSV file format
**Solution**: Verify headers and encoding

### Many Validation Errors
**Check**: Data quality in CSV
**Solution**: Review and fix data issues

### Duplicate Submissions High
**Check**: Importing same month twice
**Solution**: Use revision workflow or skip

### Import Slow
**Check**: File size and row count
**Solution**: Split large files into smaller batches

### Projects Not Appearing
**Check**: Import status and batch details
**Solution**: Verify import completed successfully

### Data Incorrect After Import
**Check**: CSV data accuracy
**Solution**: Use revision workflow to correct

---

## Contact and Support

### System Issues
- Check import history for error details
- Review audit log for operation failures
- Verify database connectivity
- Check API endpoint status

### Data Issues
- Review validation errors in preview
- Check CSV file for formatting issues
- Verify project codes exist
- Use revision workflow for corrections

### Escalation
- Document issue with screenshots
- Include batch ID and timestamps
- Provide error messages
- Contact system administrator

---

## Appendix: CSV Templates

### Template 1: New Projects
```csv
project_code,project_name,ministry,sector,state,implementing_agency,department,sanctioned_cost,approved_date,original_completion_date
P-YYYY-NNN,Project Name,Ministry Name,Sector Name,State Name,Agency Name,Department Name,Cost,YYYY-MM-DD,YYYY-MM-DD
```

### Template 2: Monthly CUF
```csv
project_code,reporting_month,revised_cost,expenditure,physical_progress,planned_completion,narrative_text
P-YYYY-NNN,YYYY-MM,Cost,Cost,Progress,YYYY-MM-DD,Narrative
```

### Template 3: Mixed
```csv
project_code,project_name,ministry,sector,state,implementing_agency,department,sanctioned_cost,approved_date,original_completion_date,reporting_month,revised_cost,expenditure,physical_progress,planned_completion,narrative_text
P-YYYY-NNN,Project Name,Ministry Name,Sector Name,State Name,Agency Name,Department Name,Cost,YYYY-MM-DD,YYYY-MM-DD,YYYY-MM,Cost,Cost,Progress,YYYY-MM-DD,Narrative
```
