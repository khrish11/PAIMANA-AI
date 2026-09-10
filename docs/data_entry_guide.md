# PAIMANA Data Entry Guide

This guide provides step-by-step instructions for operators to enter data into PAIMANA through the frontend interface.

---

## Table of Contents
1. [New Project Creation](#new-project-creation)
2. [Monthly CUF Submission](#monthly-cuf-submission)
3. [Data Revision](#data-revision)
4. [Bulk CSV Import](#bulk-csv-import)
5. [Common Data Entry Issues](#common-data-entry-issues)
6. [Data Validation Rules](#data-validation-rules)

---

## New Project Creation

### When to Create a New Project
- New infrastructure project approved
- Project not previously in PAIMANA system
- Project requires ongoing monitoring

### Step-by-Step Instructions

#### 1. Access the New Project Form
- Navigate to `/data-management`
- Click the "Add Project" button
- Or navigate directly to `/projects/new`

#### 2. Step 1: Project Information
Fill in the following fields:

**Project Code (Required)**
- Unique identifier for the project
- Format: P-YYYY-NNN (e.g., P-2026-001)
- Must be unique across all projects
- Cannot be changed after creation

**Project Name (Required)**
- Full official name of the project
- Use standard naming convention
- Example: "National Highway NH-48 Expansion"

**Department (Optional)**
- Department responsible for the project
- Example: "Transport Department"

**Ministry (Required)**
- Select from dropdown:
  - Ministry of Road Transport
  - Ministry of Railways
  - Ministry of Power
  - Ministry of Water Resources
  - Other (as configured)

**Sector (Required)**
- Select from dropdown:
  - Roads
  - Railways
  - Power
  - Water
  - Other (as configured)

**State (Required)**
- Select state where project is located
- Example: Maharashtra, Karnataka, etc.

**Implementing Agency (Required)**
- Agency executing the project
- Example: NHAI, PWD, State Electricity Board

Click "Next" to proceed.

#### 3. Step 2: Cost Information

**Sanctioned Cost (Required)**
- Initial approved cost in ₹ Crores
- Enter as number (e.g., 1000.50)
- Must be non-negative
- Use decimal for precise values

Click "Next" to proceed.

#### 4. Step 3: Schedule Information

**Approval Date (Required)**
- Date when project was officially approved
- Format: YYYY-MM-DD
- Example: 2025-01-15

**Original Completion Date (Required)**
- Initially planned completion date
- Format: YYYY-MM-DD
- Must be after approval date

**Revised Completion Date (Optional)**
- Updated completion date if schedule revised
- Format: YYYY-MM-DD
- Leave blank if not revised

Click "Next" to proceed.

#### 5. Step 4: Monitoring Information
- Initial monitoring data can be added later
- Click "Next" to skip for now

#### 6. Step 5: Review and Submit
- Review all entered information
- Click "Create Project" to submit
- Wait for confirmation message

#### 7. Verify Creation
- Success message displays:
  - Project ID
  - Project Code
  - Created At timestamp
  - Data Source
  - Audit ID
- Navigate to data management to verify project appears

### Tips for New Project Creation
- Use consistent project code format
- Verify project code is unique before submission
- Double-check dates for accuracy
- Ensure cost is in correct units (₹ Crores)

---

## Monthly CUF Submission

### When to Submit CUF
- Monthly progress reporting
- After each month's progress is recorded
- When expenditure or progress changes

### Step-by-Step Instructions

#### 1. Access the CUF Entry Form
- Navigate to `/data-entry`
- Or click "Add Monthly Update" from project detail

#### 2. Fill Submission Form

**Project ID (Required)**
- Select existing project from dropdown
- Project must exist before adding CUF

**Reporting Month (Required)**
- Select month for this submission
- Format: YYYY-MM (e.g., 2026-08)
- Cannot submit for past months if already submitted
- Future months allowed

**Revised Cost (Optional)**
- Updated cost if revised
- Enter in ₹ Crores
- Leave blank if no change

**Expenditure (Optional)**
- Actual expenditure to date
- Enter in ₹ Crores
- Must be non-negative
- Leave blank if not available

**Physical Progress (Required)**
- Percentage of project complete
- Range: 0 to 100
- Enter as number (e.g., 45.5)
- Must be between 0 and 100

**Planned Completion (Optional)**
- Updated completion date if changed
- Format: YYYY-MM-DD
- Leave blank if no change

**Narrative Text (Optional)**
- Contextual information about progress
- Explain delays, achievements, issues
- Free-form text field

**Revision Reason (Optional)**
- Only required when revising existing month
- Explain why revision is necessary
- Example: "Corrected expenditure figure"

#### 3. Validate and Submit
- Click "Submit"
- Frontend validates required fields
- Server validates data ranges
- System checks for duplicate month

#### 4. Handle Duplicate Month (if applicable)
If the reporting month already exists:
- Dialog appears with warning
- Two options:
  1. **Revise Existing**: Provide revision reason (required)
  2. **Cancel**: Abort submission
- Revision reason must be entered to proceed with revision

#### 5. Verify Success
Success message displays:
- Submission ID
- Status (created or revised)
- Version number
- Data Refresh Status:
  - ✓ Data Saved to PostgreSQL
  - ✓ DCS Updated (with score)
  - ✓ Risk Score Updated (with score)
  - ✓ Anomalies Detected (with count)
  - ✓ Governance Status
  - ✓ Audit Event Recorded

### Tips for CUF Submission
- Submit CUF regularly each month
- Use accurate physical progress percentages
- Provide narrative for significant changes
- Review duplicate month dialog carefully
- Keep revision reasons descriptive

---

## Data Revision

### When to Revise Data
- Correcting data entry errors
- Updating previously submitted figures
- Changing cost or progress after submission

### Step-by-Step Instructions

#### 1. Access Revision Workflow
- Navigate to `/data-entry`
- Select project and reporting month to revise
- Or use project history to select specific submission

#### 2. Enter New Values
- Update any fields that need correction
- All fields are optional for revision
- Only changed fields will be updated

#### 3. Provide Revision Reason (Required)
- Explain why revision is necessary
- Examples:
  - "Corrected expenditure figure from 500 to 520"
  - "Updated progress after site verification"
  - "Fixed data entry error"
- This is mandatory for all revisions

#### 4. Submit Revision
- Click "Revise Existing Submission"
- System creates new version
- Original version is preserved

#### 5. Verify Versioning
- Success message shows new version number
- Original version marked as superseded
- New version marked as latest
- Revision reason stored in audit log

#### 6. View Revision History
- Go to project detail → Version History
- Navigate to `/projects/{id}/history`
- View all versions with:
  - Version number
  - Superseded status
  - Revision reason
  - Timestamps
  - Before/after values

### Revision Best Practices
- Always provide clear revision reasons
- Revise only when necessary
- Review history before revising
- Keep audit trail complete
- Verify changes after revision

---

## Bulk CSV Import

### When to Use Bulk Import
- Importing multiple projects at once
- Importing monthly data for many projects
- Initial data load
- Regular monthly batch updates

### CSV Format Requirements

#### For New Projects
Required columns:
```
project_code,project_name,ministry,sector,state,implementing_agency,department,sanctioned_cost,approved_date,original_completion_date
```

Example:
```csv
project_code,project_name,ministry,sector,state,implementing_agency,department,sanctioned_cost,approved_date,original_completion_date
P-2026-001,NH-48 Expansion,Ministry of Road Transport,Roads,Maharashtra,NHAI,Transport,1000,2025-01-15,2027-12-31
P-2026-002,Railway Electrification,Ministry of Railways,Railways,Karnataka,SWR,Transport,500,2025-03-01,2026-12-31
```

#### For Monthly CUF Submissions
Required columns:
```
project_code,reporting_month,revised_cost,expenditure,physical_progress,planned_completion,narrative_text
```

Example:
```csv
project_code,reporting_month,revised_cost,expenditure,physical_progress,planned_completion,narrative_text
P-2026-001,2026-08,1050,500,45,2028-03-31,Progress on track
P-2026-002,2026-08,,300,60,,Ahead of schedule
```

### Step-by-Step Instructions

#### 1. Access Bulk Import
- Navigate to `/data-import`

#### 2. STEP 1: Upload File
- Click "Select CSV File"
- Choose CSV file from local system
- System reads file content automatically
- Supported format: CSV only

#### 3. STEP 2: Validate & Preview
- Click "Validate & Preview"
- System parses and validates CSV
- Preview displays summary:
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

#### 4. STEP 3: Review Preview
- Check validation errors carefully
- Review preview rows for correctness
- Note duplicate submissions count
- Verify data looks correct

#### 5. Handle Duplicates (if applicable)
If duplicate submissions detected:
- Check "Allow revisions" checkbox
- Revisions will be created for duplicates
- Revision reason will be "Bulk import revision"
- Without this checkbox, duplicates will be skipped

#### 6. STEP 4: Confirm Import
- Click "Confirm Import" only if preview is correct
- This is the point of no return
- Transaction will begin

#### 7. STEP 5: Import Execution
- Transaction begins
- New projects created
- New submissions created
- Revisions created (if allowed)
- Invalid rows skipped
- Transaction commits on success
- Transaction rolls back on failure

#### 8. STEP 6: Verify Results
Success message displays:
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

Navigate to:
- Data management to verify projects
- Import history to view batch details

### Bulk Import Tips
- Validate CSV format before upload
- Use preview to catch errors early
- Handle duplicates appropriately
- Keep CSV files organized
- Use descriptive batch names

---

## Common Data Entry Issues

### Issue: Project Code Already Exists
**Cause**: Project code must be unique
**Solution**: Choose a different project code
**Prevention**: Check existing codes before creating

### Issue: Duplicate Reporting Month
**Cause**: Month already submitted for this project
**Solution**: Use revision workflow with reason
**Prevention**: Check submission history before entry

### Issue: Physical Progress Out of Range
**Cause**: Value not between 0 and 100
**Solution**: Enter valid percentage (0-100)
**Prevention**: Verify data before entry

### Issue: Negative Expenditure
**Cause**: Expenditure cannot be negative
**Solution**: Enter non-negative value
**Prevention**: Check data source for errors

### Issue: Invalid Date Format
**Cause**: Date not in YYYY-MM-DD format
**Solution**: Use correct format
**Prevention**: Follow date format consistently

### Issue: Project Not Found
**Cause**: Project ID doesn't exist
**Solution**: Create project first or verify ID
**Prevention**: Use project code from dropdown

### Issue: CSV Validation Errors
**Cause**: CSV format incorrect or data invalid
**Solution**: Fix CSV and re-import
**Prevention**: Validate CSV before upload

### Issue: Transaction Failed
**Cause**: Import error during transaction
**Solution**: Fix data and re-import
**Prevention**: Review preview carefully

---

## Data Validation Rules

### Frontend Validation
- Required fields checked
- Numeric ranges validated
- Date formats verified
- Progress range (0-100)
- Non-negative costs

### Server-Side Validation
- All frontend validation repeated
- Project existence verified
- Duplicate month detection
- Data type checking
- Business rule enforcement
- Role-based access control

### Validation Error Messages
- Clear, actionable error messages
- Field-specific errors
- Guidance for correction
- Examples of valid values

### Validation Best Practices
- Validate before submission
- Review error messages carefully
- Fix all errors before resubmitting
- Use preview for bulk imports
- Keep data clean and accurate

---

## Data Entry Checklist

### Before Submission
- [ ] All required fields filled
- [ ] Data validated for accuracy
- [ ] Numeric ranges verified
- [ ] Dates in correct format
- [ ] Project code unique (for new projects)
- [ ] Reporting month not duplicate (unless revising)

### After Submission
- [ ] Success message received
- [ ] Data refresh status verified
- [ ] Audit ID recorded
- [ ] Dashboard updated
- [ ] Project detail verified

### For Bulk Import
- [ ] CSV format validated
- [ ] Preview reviewed carefully
- [ ] Duplicates handled appropriately
- [ ] Transaction status verified
- [ ] Import history checked

---

## Getting Help

### Common Issues Resolution
1. Check error messages for specific guidance
2. Review this guide for relevant sections
3. Check audit log for operation details
4. Contact system administrator if needed

### Support Resources
- Continuous Operations Runbook
- Monthly Import Guide
- Revision and Versioning Documentation
- System Administrator Contact

---

## Data Entry Best Practices

### Accuracy
- Double-check all numeric entries
- Verify dates before submission
- Use official project names
- Keep data sources documented

### Consistency
- Use standard naming conventions
- Follow consistent date formats
- Maintain regular submission schedule
- Use descriptive revision reasons

### Documentation
- Provide narrative for significant changes
- Document reasons for revisions
- Keep audit trail complete
- Maintain data quality

### Quality
- Validate data before submission
- Review preview before bulk import
- Monitor data quality metrics
- Address issues promptly
