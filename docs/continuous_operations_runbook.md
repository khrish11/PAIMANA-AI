# PAIMANA Continuous Operations Runbook

This runbook documents the operational procedures for maintaining PAIMANA month after month without requiring developer involvement.

## Overview

PAIMANA is designed to be continuously updatable through:
- New project creation
- Monthly CUF submissions
- Bulk CSV imports
- Data revisions with versioning
- Automatic intelligence recalculation
- Audit logging

All operations are performed through the frontend interface with PostgreSQL persistence.

---

## NEW PROJECT CREATION

### Prerequisites
- Valid project code (unique identifier)
- Project metadata (name, ministry, sector, state, implementing agency)
- Sanctioned cost (₹ Crores)
- Approval date
- Original completion date

### Procedure

1. **Navigate to Data Management**
   - Go to `/data-management`
   - Click "Add Project"

2. **Fill Project Information (Step 1 of 5)**
   - Project Code: Unique identifier (e.g., P-2026-001)
   - Project Name: Full project name
   - Department: Department responsible
   - Ministry: Select from dropdown
   - Sector: Select from dropdown (Roads, Railways, Power, Water)
   - State: Select from dropdown
   - Implementing Agency: Agency name

3. **Fill Cost Information (Step 2 of 5)**
   - Sanctioned Cost: Initial approved cost in ₹ Crores

4. **Fill Schedule Information (Step 3 of 5)**
   - Approval Date: Date of project approval
   - Original Completion Date: Initially planned completion
   - Revised Completion Date: Optional, if schedule has been revised

5. **Review and Submit (Step 4-5)**
   - Review all entered information
   - Click "Create Project"

6. **Verify Creation**
   - Success message displays with:
     - Project ID
     - Project Code
     - Created At timestamp
     - Data Source (manual)
     - Audit ID
   - Navigate to data management to verify project appears in list

7. **Post-Creation Actions**
   - Dashboard automatically updates with new project count
   - Project list cache invalidated
   - Audit log entry created for CREATE_PROJECT operation

### Troubleshooting

**Error: Project code already exists**
- Choose a different project code
- Project codes must be unique across all projects

**Error: Required field missing**
- Ensure all required fields are filled
- Check form validation error messages

**Error: Invalid date format**
- Use YYYY-MM-DD format for date fields
- Ensure dates are realistic (e.g., approval before completion)

---

## MONTHLY CUF SUBMISSION

### Prerequisites
- Project must exist in system
- Valid reporting month (YYYY-MM format)
- Physical progress (0-100%)
- Expenditure (₹ Crores, non-negative)
- Optional: Revised cost, planned completion, narrative

### Procedure

1. **Navigate to Data Entry**
   - Go to `/data-entry`
   - Or click "Add Monthly Update" from project detail

2. **Fill Submission Form**
   - Project ID: Select existing project
   - Reporting Month: Select month (e.g., 2026-08)
   - Revised Cost: Optional, if cost has been revised
   - Expenditure: Actual expenditure to date
   - Physical Progress: Percentage complete (0-100)
   - Planned Completion: Optional, updated completion date
   - Narrative Text: Optional, contextual information

3. **Validate**
   - Frontend validates required fields
   - Checks numeric ranges (progress 0-100, non-negative costs)
   - Server-side validation also performed

4. **Submit**
   - Click "Submit"
   - System checks for duplicate reporting month

5. **Handle Duplicate Month (if applicable)**
   - If month already exists, dialog appears
   - Options:
     - **Revise Existing**: Provide revision reason (required)
     - **Cancel**: Abort submission
   - Revision reason is mandatory for revisions

6. **Verify Success**
   - Success message displays with:
     - Submission ID
     - Status (created or revised)
     - Version number
     - Data Refresh Status:
       - ✓ Data Saved to PostgreSQL
       - ✓ DCS Updated
       - ✓ Risk Score Updated
       - ✓ Anomalies Detected
       - ✓ Governance Status
       - ✓ Audit Event Recorded

7. **Automatic Intelligence Refresh**
   - DCS (Data Confidence Score) recalculated
   - Risk score recalculated
   - Anomaly detection run
   - ML inference refreshed (using frozen v2 models)
   - SHAP explanations refreshed
   - Governance eligibility checked
   - All refresh operations logged

### Troubleshooting

**Error: Duplicate reporting month**
- Use revision workflow with reason
- Or cancel and select different month

**Error: Physical progress out of range**
- Must be between 0 and 100
- Check for data entry errors

**Error: Negative expenditure**
- Expenditure cannot be negative
- Verify data entry

**Error: Project not found**
- Ensure project ID is correct
- Project must exist before adding CUF

---

## REVISION WORKFLOW

### When to Revise
- Correcting data entry errors
- Updating previously submitted month
- Changing cost or progress figures

### Procedure

1. **Navigate to Data Entry**
   - Go to `/data-entry`
   - Select project and reporting month to revise

2. **Enter New Values**
   - Update fields as needed
   - All fields optional for revision

3. **Provide Revision Reason (Required)**
   - Explain why revision is necessary
   - Examples: "Corrected expenditure figure", "Updated progress after site visit"

4. **Submit Revision**
   - Click "Revise Existing Submission"
   - System creates new version

5. **Verify Versioning**
   - Original version preserved (superseded)
   - New version marked as latest
   - Version number incremented
   - Superseded timestamp recorded
   - Revision reason stored in audit log

6. **View History**
   - Go to project detail → Version History
   - Or navigate to `/projects/{id}/history`
   - View all versions with:
     - Version number
     - Superseded status
     - Revision reason
     - Timestamps

### Version Preservation Rules
- Original values never destroyed
- All historical versions accessible
- Latest version used for intelligence calculations
- Audit trail complete for all revisions

---

## BULK CSV IMPORT

### Prerequisites
- CSV file with proper format
- Headers must match expected columns
- Valid data in all fields

### CSV Format Requirements

**For New Projects:**
```
project_code,project_name,ministry,sector,state,implementing_agency,department,sanctioned_cost,approved_date,original_completion_date
P-2026-001,Sample Road Project,Ministry of Road Transport,Roads,Maharashtra,NHAI,Transport,1000,2025-01-15,2027-12-31
```

**For Monthly CUF Submissions:**
```
project_code,reporting_month,revised_cost,expenditure,physical_progress,planned_completion,narrative_text
P-2026-001,2026-08,1050,500,45,2028-03-31,Progress on track
```

### Procedure

1. **Navigate to Data Import**
   - Go to `/data-import`

2. **STEP 1: Upload File**
   - Click "Select CSV File"
   - Choose CSV file from local system
   - System reads file content

3. **STEP 2: Validate & Preview**
   - Click "Validate & Preview"
   - System parses and validates CSV
   - Preview displays:
     - Rows Detected
     - New Projects
     - New Submissions
     - Existing Projects
     - Duplicate Submissions
     - Revisions
     - Invalid Rows
     - Missing Fields
   - Validation errors shown in table
   - Preview rows displayed (first 10)

4. **STEP 3: Review Preview**
   - Check validation errors
   - Review preview rows for correctness
   - Note duplicate submissions

5. **Handle Duplicates (if applicable)**
   - If duplicate submissions detected:
     - Check "Allow revisions" checkbox
     - Revisions will be created for duplicates
     - Revision reason will be "Bulk import revision"

6. **STEP 4: Confirm Import**
   - Click "Confirm Import" only if preview is correct
   - System executes transactional import

7. **STEP 5: Import Execution**
   - Transaction begins
   - New projects created
   - New submissions created
   - Revisions created (if allowed)
   - Invalid rows skipped
   - Transaction commits on success
   - Transaction rolls back on failure

8. **STEP 6: Verify Results**
   - Success message displays:
     - Batch ID
     - Status (completed/failed)
     - Rows Detected
     - New Projects
     - Existing Projects
     - New Submissions
     - Duplicate Submissions
     - Revisions
     - Invalid Rows
     - Started/Completed timestamps
   - Navigate to data management to verify
   - Navigate to import history to view batch details

### Idempotency
- Uploading the same CSV twice creates no duplicate records
- Second import shows:
  - New: 0
  - Already Existing: N
  - Revised: 0
  - Invalid: 0

### Transaction Safety
- All-or-nothing import
- If any row fails, entire batch rolls back
- No partial imports
- Clear error messages on failure

### Troubleshooting

**Error: Invalid CSV format**
- Check CSV headers match expected format
- Ensure proper delimiter (comma)
- Remove extra spaces or special characters

**Error: Missing required fields**
- Verify all required columns present
- Check for empty required values

**Error: Project code not found**
- For submissions, project must exist
- Create project first or include in CSV

**Error: Transaction failed**
- Check error message for specific issue
- Fix data and re-import
- Transaction rolled back, no changes made

---

## IMPORT HISTORY

### Viewing Import History

1. **Navigate to Import History**
   - Go to `/data-import/history`
   - Or click "View Import History" after import

2. **Filter by Status**
   - All: Show all imports
   - Completed: Successful imports only
   - Failed: Failed imports only
   - In Progress: Currently running

3. **View Batch Details**
   - Each batch shows:
     - Batch ID
     - Batch Name
     - Status
     - Rows Processed
     - New Projects
     - New Submissions
     - Revisions
     - Invalid Rows
     - Created By
     - Completed At

4. **Audit Trail**
   - All imports logged in audit table
   - Includes user, timestamp, operation details
   - Persists across backend restarts

---

## INTELLIGENCE REFRESH

### Automatic Refresh Triggers
- New project creation
- New CUF submission
- CUF revision
- Bulk import completion

### Refresh Operations
1. **DCS (Data Confidence Score)**
   - Recalculated based on data quality
   - Considers completeness, timeliness, consistency

2. **Risk Score**
   - Recalculated using ML model
   - Components: cost risk, schedule risk, progress anomaly, governance risk

3. **Anomaly Detection**
   - Statistical analysis of progress vs. expected
   - Cost overrun detection
   - Schedule delay detection

4. **ML Inference**
   - Uses frozen v2 models
   - Not automatically retrained
   - Retrain only after sufficient validated outcomes

5. **SHAP Explanations**
   - Feature importance for risk prediction
   - Refreshed after ML inference

6. **Governance Eligibility**
   - Check if project meets governance thresholds
   - Based on risk triggers and milestones

### Refresh Status Display
After CUF submission, refresh status shows:
- ✓ Data Saved to PostgreSQL
- ✓ DCS Updated (with score)
- ✓ Risk Score Updated (with score)
- ✓ Anomalies Detected (with count)
- ✓ Governance Status (status)
- ✓ Audit Event Recorded

### Background Processing
- Fast operations: database write, validation, basic risk update
- Background operations: large anomaly recomputation, RCF refresh, PBE, embeddings, NID, PDR clustering
- Status displayed as: Queued, Running, Complete, Failed

---

## AUDIT LOGGING

### Logged Operations
- CREATE_PROJECT
- CREATE_CUF_SUBMISSION
- REVISE_CUF_SUBMISSION
- BULK_IMPORT
- RISK_RECALCULATION
- MODEL_INFERENCE
- DATA_REFRESH

### Audit Information
- Operation type
- Entity type and ID
- User who performed operation
- User role
- Timestamp
- Before/after state (for revisions)
- Source (manual, bulk import)

### Viewing Audit
- Audit persists in PostgreSQL
- Survives backend restarts
- Can be queried for compliance
- Complete trail of all data changes

---

## DATA PROVENANCE

### Provenance Information
- Data Source (manual, bulk import)
- Source File (for imports)
- Reporting Month
- Entered By
- Imported At
- Mapping Method

### Viewing Provenance
- Project detail page shows provenance section
- Includes data source, latest month, last updated, import method
- Historical submissions show provenance in history view

---

## MONTHLY OPERATIONS CHECKLIST

### Before Month Close
- [ ] All CUF submissions received for the month
- [ ] Data validated for completeness
- [ ] Anomalies reviewed and addressed
- [ ] Risk scores reviewed
- [ ] Governance queue processed

### During Month Close
- [ ] Bulk import completed (if applicable)
- [ ] Individual submissions completed
- [ ] Revisions processed with reasons
- [ ] Intelligence refresh verified
- [ ] Dashboard updated

### After Month Close
- [ ] Reports generated with latest data
- [ ] Audit log reviewed
- [ ] Import history verified
- [ ] Data quality metrics checked
- [ ] Backup confirmed

---

## MODEL OPERATIONS

### Monthly Data Updates
- ML inference runs automatically on new data
- Uses frozen v2 models
- No automatic retraining

### Model Retraining Policy
- Retrain only after sufficient validated outcomes
- Evaluate new model before promotion
- Manual approval required for model updates
- Version tracking for all model changes

### Model Versioning
- Current model version displayed in UI
- Model transparency section shows:
  - Model name
  - Prediction timestamp
  - Last data update
  - Confidence score
  - Source

---

## DATA QUALITY MONITORING

### Quality Metrics
- Sector coverage
- Ministry coverage
- Agency coverage
- State coverage
- Narrative coverage
- Completed outcomes
- Duplicates
- Conflicts
- Latest refresh
- Validation errors

### Viewing Data Health
- Navigate to `/data-health`
- Metrics update after each import
- Identify gaps in data coverage
- Track validation issues

---

## ROLE-BASED ACCESS CONTROL

### Roles and Permissions

**VIEWER**
- Read-only access
- Cannot create or edit data
- View dashboards and reports

**AGENCY**
- Can edit only authorized projects
- Create new projects
- Submit CUF for own projects
- Cannot edit other agencies' projects

**ANALYST**
- Read and analytics access
- View all data
- Generate reports
- Cannot modify data

**REVIEWER/IPMD**
- Governance and data actions
- Review risk assessments
- Approve governance actions
- Limited data editing

**ADMIN**
- Full data administration
- All permissions
- System configuration

### Testing RBAC
- Verify role restrictions independently
- Test backend authorization
- Ensure frontend respects permissions

---

## EMERGENCY PROCEDURES

### Import Failure
- Check error message for specific issue
- Fix CSV data
- Re-import with corrected file
- Transaction rolled back, no data loss

### System Error During Submission
- Check audit log for partial operations
- Verify data integrity
- Re-submit if necessary
- Contact support if issue persists

### Data Inconsistency Detected
- Review import history
- Check revision history
- Identify source of inconsistency
- Use revision workflow to correct

### Backup and Recovery
- PostgreSQL backups maintained
- Audit log provides recovery trail
- Historical versions preserved
- No data deletion without audit

---

## CONTACT AND SUPPORT

### System Issues
- Check backend logs
- Review audit log for errors
- Verify database connectivity
- Check API endpoint status

### Data Issues
- Review import history
- Check validation errors
- Verify data quality metrics
- Use revision workflow to correct

### Escalation
- Document issue with screenshots
- Include audit IDs and timestamps
- Provide error messages
- Contact system administrator

---

## BEST PRACTICES

### Data Entry
- Validate data before submission
- Use descriptive revision reasons
- Review preview before bulk import
- Keep audit trail complete

### Monthly Operations
- Process submissions promptly
- Review anomalies regularly
- Monitor data quality metrics
- Generate reports after month close

### System Maintenance
- Monitor refresh job status
- Review audit logs periodically
- Check data health metrics
- Plan model retraining appropriately

---

## VERSION HISTORY

- v1.0 - Initial runbook for continuous operations
- Covers all data entry workflows
- Includes troubleshooting procedures
- Documents audit and provenance features
