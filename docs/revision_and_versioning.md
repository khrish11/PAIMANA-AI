# PAIMANA Revision and Versioning Documentation

This document explains the revision and versioning system in PAIMANA, including how data changes are tracked, historical values are preserved, and the audit trail is maintained.

---

## Overview

PAIMANA implements a comprehensive revision and versioning system to ensure:

- **No silent overwrites**: Data is never overwritten without explicit user action
- **Historical preservation**: All previous versions of data are retained
- **Complete audit trail**: Every change is logged with context
- **Version tracking**: Clear version numbers and lineage
- **Revision reasons**: Mandatory explanations for all revisions

---

## Versioning Model

### CUF Submission Versioning

Each CUF (Critical Update Form) submission can have multiple versions:

- **Version 1**: Original submission
- **Version 2+**: Revisions to the original
- **Latest Flag**: Indicates which version is currently active
- **Superseded By**: Points to the newer version
- **Superseded At**: Timestamp when version was superseded
- **Superseded Reason**: Explanation for the revision

### Version States

| State | Description | Used For Intelligence |
|-------|-------------|----------------------|
| Latest | Most recent version | Yes - used for all calculations |
| Superseded | Previous version | No - historical only |
| Deleted | Soft-deleted (if implemented) | No |

### Version Lineage

```
Version 1 (Original)
  ↓ superseded_by → Version 2
    ↓ superseded_by → Version 3 (Latest)
```

---

## Revision Workflow

### When Revisions Occur

Revisions are triggered when:
1. User submits CUF for a reporting month that already exists
2. User explicitly chooses to revise existing submission
3. Bulk import with "Allow revisions" enabled
4. Data correction through admin interface

### Revision Process

#### Step 1: Duplicate Detection
- System checks for existing submission with same project_id and reporting_month
- If found, presents duplicate dialog to user

#### Step 2: User Decision
- User chooses between:
  - **Revise Existing**: Create new version with reason
  - **Cancel**: Abort submission

#### Step 3: Revision Reason (Required)
- User must provide explanation for revision
- Examples:
  - "Corrected expenditure figure from 500 to 520"
  - "Updated progress after site verification"
  - "Fixed data entry error in physical progress"

#### Step 4: Version Creation
- New version created with incremented version number
- Previous version marked as superseded
- Superseded_by field updated
- Superseded_at timestamp recorded
- Superseded_reason stored

#### Step 5: Intelligence Refresh
- Risk score recalculated using new version
- DCS updated
- Anomalies re-detected
- ML inference refreshed
- SHAP explanations regenerated

#### Step 6: Audit Logging
- REVISE_CUF_SUBMISSION operation logged
- Before/after values recorded
- User and timestamp captured
- Revision reason stored

---

## Data Preservation

### What Is Preserved

For each revision, the following is preserved:

1. **Original Version**
   - All field values from original submission
   - Original submission timestamp
   - Original submitted_by user
   - Original data source

2. **Revision Metadata**
   - Version number
   - Superseded timestamp
   - Superseded reason
   - User who made revision
   - Data source of revision

3. **Audit Trail**
   - Operation type (REVISE_CUF_SUBMISSION)
   - Entity ID (submission_id)
   - User who performed operation
   - Timestamp of operation
   - Before state (original values)
   - After state (new values)
   - Reason for revision

### What Is NOT Destroyed

- Original submission data (ever)
- Revision history (ever)
- Audit log entries (ever)
- Version lineage information (ever)

### Data Retention Policy

- **Historical versions**: Retained indefinitely
- **Audit logs**: Retained indefinitely
- **Revision reasons**: Retained indefinitely
- **Before/after states**: Retained indefinitely

---

## Viewing Revision History

### Project History Page

Navigate to `/projects/{id}/history` to view:

#### Timeline View
- All submissions for the project
- Ordered by reporting month (descending)
- Shows version number for each month
- Indicates latest vs. superseded versions

#### Table Columns
- **Reporting Month**: YYYY-MM format
- **Version**: Version number with status badge
- **Physical Progress**: Percentage complete
- **Expenditure**: ₹ Crores
- **Revised Cost**: ₹ Crores (if applicable)
- **Planned Completion**: Date (if applicable)
- **Submitted By**: User who submitted
- **Submitted At**: Timestamp
- **Data Source**: manual, bulk_import, etc.
- **Superseded**: Yes/No with details
  - Superseded timestamp
  - Superseded reason

#### Narrative History
- Separate section showing narrative text for each submission
- Useful for understanding context of changes
- Shows revision reasons for superseded versions

### Version Badges

- **v1 (Latest)**: Original and still current
- **v2 (Latest)**: Revised and current
- **v1 (Superseded)**: Original, replaced by v2
- **v2 (Superseded)**: First revision, replaced by v3

---

## Revision Scenarios

### Scenario 1: Data Entry Error

**Situation**: User entered wrong expenditure figure

**Original Version (v1)**
- Expenditure: 500.00
- Physical Progress: 45.0
- Submitted: 2026-08-01

**Revision (v2)**
- Expenditure: 520.00 (corrected)
- Physical Progress: 45.0 (unchanged)
- Revision Reason: "Corrected expenditure figure from 500 to 520"
- Superseded: v1

**Result**
- v1 preserved with original values
- v2 created with corrected values
- v2 marked as latest
- Audit log records change
- Intelligence recalculated with v2

### Scenario 2: Progress Update

**Situation**: Progress increased, need to update

**Original Version (v1)**
- Physical Progress: 45.0
- Expenditure: 500.00
- Submitted: 2026-08-01

**Revision (v2)**
- Physical Progress: 50.0 (updated)
- Expenditure: 520.00 (also updated)
- Revision Reason: "Updated progress after site verification"
- Superseded: v1

**Result**
- Both fields updated
- Version 2 reflects current state
- Version 1 preserved for historical comparison

### Scenario 3: Multiple Revisions

**Situation**: Multiple corrections over time

**Version 1 (Original)**
- Expenditure: 500.00
- Progress: 45.0
- Submitted: 2026-08-01

**Version 2 (First Revision)**
- Expenditure: 520.00
- Progress: 45.0
- Reason: "Corrected expenditure"
- Superseded: v1

**Version 3 (Second Revision)**
- Expenditure: 520.00
- Progress: 50.0
- Reason: "Updated progress"
- Superseded: v2

**Result**
- Complete lineage: v1 → v2 → v3
- All versions preserved
- v3 marked as latest
- Full audit trail available

---

## Bulk Import Revisions

### Revision Handling in Bulk Import

When importing CSV with duplicate months:

#### Option A: Allow Revisions
- Check "Allow revisions" checkbox
- System creates revisions for all duplicates
- Revision reason: "Bulk import revision"
- Original versions preserved
- New versions marked as latest

#### Option B: Skip Duplicates
- Leave checkbox unchecked
- Duplicate rows skipped
- No revisions created
- Original data unchanged

### Idempotency with Revisions

- First import: Creates v1 for all submissions
- Second import (same data): Shows "Already Existing", no changes
- Second import (different data): Creates v2 revisions if allowed

---

## Audit Trail

### Audit Log Structure

Each revision creates an audit log entry:

```json
{
  "audit_id": "uuid",
  "operation": "REVISE_CUF_SUBMISSION",
  "entity_type": "cuf_submission",
  "entity_id": "submission_id",
  "user": "username",
  "role": "agency",
  "timestamp": "2026-08-15T10:30:00Z",
  "before_state": {
    "expenditure": 500.00,
    "physical_progress": 45.0
  },
  "after_state": {
    "expenditure": 520.00,
    "physical_progress": 45.0
  },
  "reason": "Corrected expenditure figure from 500 to 520",
  "source": "manual"
}
```

### Querying Audit Trail

Audit logs can be queried for:
- All revisions by a user
- All revisions for a project
- All revisions within a time range
- Revisions with specific reasons

### Audit Persistence

- Audit logs persist in PostgreSQL
- Survive backend restarts
- Cannot be deleted through UI
- Complete compliance trail

---

## Intelligence Recalculation

### What Gets Recalculated

After a revision, the following are recalculated:

1. **DCS (Data Confidence Score)**
   - Based on new data values
   - Considers data quality metrics

2. **Risk Score**
   - Recalculated using ML model
   - Components updated based on new values

3. **Anomaly Detection**
   - Re-run with new data
   - New anomalies may be detected
   - Previous anomalies may be resolved

4. **ML Inference**
   - Refreshed with new feature values
   - Uses frozen v2 models
   - SHAP explanations regenerated

5. **Governance Eligibility**
   - Re-evaluated with new risk scores
   - Governance queue updated if needed

### Historical Intelligence

- Historical intelligence based on historical data
- Each version's intelligence calculated at time of submission
- Historical intelligence not recalculated retroactively
- Current intelligence always based on latest version

---

## Best Practices

### When to Revise
- Correcting data entry errors
- Updating with verified correct data
- Incorporating official corrections
- Addressing validation issues

### When NOT to Revise
- Minor cosmetic changes
- Temporary updates
- Uncertain corrections
- Without proper verification

### Revision Reasons
- Be specific and descriptive
- Include before/after values when relevant
- Explain why correction is necessary
- Reference source of correction if applicable

### Examples of Good Revision Reasons
- "Corrected expenditure from 500 to 520 based on verified accounts"
- "Updated physical progress to 50% after site inspection on 2026-08-10"
- "Fixed data entry error: progress was 45, should be 54"
- "Revised cost to 1050 Cr per official order dated 2026-08-05"

### Examples of Poor Revision Reasons
- "Update"
- "Correction"
- "Fix"
- "Changed"

---

## Technical Implementation

### Database Schema

#### CUFSubmission Table
```sql
- submission_id (UUID, PK)
- project_id (FK)
- reporting_month (Date)
- version (Integer)
- is_latest (Boolean)
- superseded_by (FK to CUFSubmission)
- superseded_at (Timestamp)
- superseded_reason (Text)
- expenditure (Numeric)
- physical_progress (Numeric)
- revised_cost (Numeric)
- planned_completion (Date)
- narrative_text (Text)
- submitted_at (Timestamp)
- submitted_by (String)
- data_source (String)
- import_method (String)
- provenance_status (String)
```

#### CUFRevision Table
```sql
- revision_id (UUID, PK)
- submission_id (FK)
- revision_number (Integer)
- field_changes (JSONB)
- reason (Text)
- revised_by (String)
- revised_at (Timestamp)
```

#### AuditLog Table
```sql
- audit_id (UUID, PK)
- operation (String)
- entity_type (String)
- entity_id (UUID)
- user (String)
- role (String)
- timestamp (Timestamp)
- before_state (JSONB)
- after_state (JSONB)
- reason (Text)
- source (String)
```

### API Endpoints

#### Create Submission (with revision support)
```
POST /api/v1/data_operations/projects/{project_id}/submissions
```
- Detects duplicates
- Returns status: "created" or "duplicate"
- If duplicate, requires revision_reason

#### Get Project History
```
GET /api/v1/data_operations/projects/{project_id}/history
```
- Returns all submissions with versions
- Ordered by reporting_month and version
- Includes superseded information

### Backend Logic

#### Duplicate Detection
```python
existing = db.query(CUFSubmission).filter(
    CUFSubmission.project_id == project_id,
    CUFSubmission.reporting_month == reporting_month,
    CUFSubmission.is_latest == True
).first()

if existing:
    return {"status": "duplicate", "existing_id": existing.submission_id}
```

#### Revision Creation
```python
# Mark existing as superseded
existing.is_latest = False
existing.superseded_by = new_submission.submission_id
existing.superseded_at = datetime.now()
existing.superseded_reason = revision_reason

# Create new version
new_submission.version = existing.version + 1
new_submission.is_latest = True
```

---

## Security and Access Control

### Revision Permissions

**AGENCY Role**
- Can revise own projects
- Cannot revise other agencies' projects
- Must provide revision reason

**ADMIN Role**
- Can revise any project
- Can override revision reason requirement
- Full revision access

**ANALYST Role**
- Read-only access to revisions
- Cannot create revisions
- Can view history

**VIEWER Role**
- Read-only access
- Cannot revise
- Limited history access

### Audit Access

**ADMIN**
- Full audit log access
- Can view all revisions
- Can export audit data

**REVIEWER/IPMD**
- Audit log access for governance
- Can view revision reasons
- Can track compliance

**Others**
- Limited audit access
- Own revisions only
- No export capability

---

## Compliance and Reporting

### Revision Reporting

Generate reports showing:
- Number of revisions per project
- Revision frequency over time
- Common revision reasons
- Users with most revisions
- Time between submission and revision

### Compliance Requirements

- All revisions must have reasons
- Audit trail must be complete
- Historical data must be preserved
- Version lineage must be traceable

### Audit Trail Verification

Regular verification of:
- Audit log completeness
- Version integrity
- Reason presence for all revisions
- Before/after state accuracy

---

## Troubleshooting

### Issue: Revision Not Allowed
**Cause**: User lacks permissions
**Solution**: Check user role and project ownership

### Issue: Revision Reason Missing
**Cause**: Revision reason not provided
**Solution**: Provide mandatory revision reason

### Issue: Version Not Incrementing
**Cause**: System error in version logic
**Solution**: Check backend logs, verify database state

### Issue: Historical Data Lost
**Cause**: Should not happen with proper implementation
**Solution**: Check database integrity, verify backup

### Issue: Audit Log Missing Entry
**Cause**: Audit logging failure
**Solution**: Check audit service, verify database connection

---

## Future Enhancements

### Potential Improvements
- Diff view between versions
- Rollback to previous version
- Approval workflow for revisions
- Revision impact analysis
- Automated revision suggestions

### Version Comparison
- Side-by-side view of versions
- Highlight changed fields
- Calculate impact on risk score
- Show intelligence changes

### Rollback Capability
- Ability to revert to previous version
- Creates new version (not destructive)
- Requires revision reason
- Audit trail maintained

---

## Summary

The PAIMANA revision and versioning system ensures:

- **Data Integrity**: No silent overwrites, explicit revisions only
- **Historical Preservation**: All versions retained indefinitely
- **Complete Audit**: Every change logged with context
- **User Accountability**: Revision reasons mandatory
- **Intelligence Accuracy**: Recalculated after each revision
- **Compliance Ready**: Full audit trail for regulatory requirements

This system allows PAIMANA to maintain accurate, traceable data while supporting the continuous update workflow required for ongoing project monitoring.
