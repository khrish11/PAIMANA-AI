import { useState } from 'react';
import { Card, Badge, Button } from '../components/common';
import { colors, spacing, typography, borderRadius } from '../tokens';
import { createSubmissionData } from '../services/api';
import { invalidateAfterSubmission, invalidateAfterRevision } from '../hooks';

function DataEntry() {
  const [formData, setFormData] = useState({
    project_id: '',
    reporting_month: '',
    revised_cost: '',
    expenditure: '',
    physical_progress: '',
    planned_completion: '',
    narrative_text: '',
    revision_reason: '',
  });
  const [validationErrors, setValidationErrors] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDuplicateDialog, setShowDuplicateDialog] = useState(false);
  const [duplicateInfo, setDuplicateInfo] = useState(null);

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
    setValidationErrors(prev => ({ ...prev, [e.target.name]: '' }));
  };

  const validate = () => {
    const errors = {};
    
    if (!formData.project_id) errors.project_id = 'Project ID is required';
    if (!formData.reporting_month) errors.reporting_month = 'Reporting month is required';
    if (formData.physical_progress === '' || formData.physical_progress === null) {
      errors.physical_progress = 'Physical progress is required';
    } else {
      const progress = parseFloat(formData.physical_progress);
      if (progress < 0 || progress > 100) {
        errors.physical_progress = 'Physical progress must be between 0 and 100';
      }
    }
    if (formData.expenditure && parseFloat(formData.expenditure) < 0) {
      errors.expenditure = 'Expenditure cannot be negative';
    }
    if (formData.revised_cost && parseFloat(formData.revised_cost) < 0) {
      errors.revised_cost = 'Revised cost cannot be negative';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    setLoading(true);
    setError(null);

    try {
      const submissionData = {
        reporting_month: formData.reporting_month ? new Date(formData.reporting_month + '-01').toISOString().split('T')[0] : null,
        revised_cost: formData.revised_cost ? parseFloat(formData.revised_cost) : null,
        expenditure: formData.expenditure ? parseFloat(formData.expenditure) : null,
        physical_progress: formData.physical_progress ? parseFloat(formData.physical_progress) : null,
        planned_completion: formData.planned_completion || null,
        narrative_text: formData.narrative_text || null,
        revision_reason: formData.revision_reason || null,
        data_source: 'manual',
        import_method: 'manual',
        provenance_status: 'verified',
      };

      const response = await createSubmissionData(formData.project_id, submissionData);
      
      // Check if it was a duplicate that requires revision
      if (response.status === 'duplicate') {
        setDuplicateInfo(response);
        setShowDuplicateDialog(true);
        setLoading(false);
        return;
      }
      
      // Invalidate caches after successful submission
      invalidateAfterSubmission(formData.project_id);
      
      setResult(response);
      setSubmitted(true);
    } catch (err) {
      const errMessage = err.message || 'Failed to submit CUF';
      
      // Check if it's a duplicate error
      if (errMessage.includes('duplicate') || errMessage.includes('already exists')) {
        setShowDuplicateDialog(true);
      } else {
        setError(errMessage);
      }
      setLoading(false);
    }
  };

  const handleRevise = async () => {
    if (!formData.revision_reason.trim()) {
      setError('Revision reason is required when revising an existing submission');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const submissionData = {
        reporting_month: formData.reporting_month ? new Date(formData.reporting_month + '-01').toISOString().split('T')[0] : null,
        revised_cost: formData.revised_cost ? parseFloat(formData.revised_cost) : null,
        expenditure: formData.expenditure ? parseFloat(formData.expenditure) : null,
        physical_progress: formData.physical_progress ? parseFloat(formData.physical_progress) : null,
        planned_completion: formData.planned_completion || null,
        narrative_text: formData.narrative_text || null,
        revision_reason: formData.revision_reason,
        data_source: 'manual',
        import_method: 'manual',
        provenance_status: 'verified',
      };

      const response = await createSubmissionData(formData.project_id, submissionData);
      
      // Invalidate caches after successful revision
      invalidateAfterRevision(formData.project_id);
      
      setResult(response);
      setSubmitted(true);
      setShowDuplicateDialog(false);
    } catch (err) {
      setError(err.message || 'Failed to revise submission');
      setLoading(false);
    }
  };

  if (submitted && result) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
        <Card padding="lg">
          <div style={{ 
            padding: spacing.md,
            backgroundColor: `${colors.accent.success}10`,
            border: `1px solid ${colors.accent.success}30`,
            borderRadius: borderRadius.md,
          }}>
            <h1 style={{ 
              fontSize: typography.fontSize['2xl'],
              fontWeight: 700,
              color: colors.accent.success,
              marginBottom: spacing.md 
            }}>
              Submission {result.status === 'revised' ? 'Revised' : 'Successful'}
            </h1>
            <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
              <div><strong>Submission ID:</strong> {result.submission_id}</div>
              <div><strong>Status:</strong> <Badge variant={result.status === 'revised' ? 'warning' : 'success'}>{result.status}</Badge></div>
              <div><strong>Message:</strong> {result.message}</div>
              <div><strong>Version:</strong> {result.version}</div>
            </div>
            
            {/* Data Refresh Status */}
            <div style={{ 
              marginTop: spacing.lg,
              padding: spacing.md,
              backgroundColor: colors.background.tertiary,
              borderRadius: borderRadius.md,
              border: `1px solid ${colors.border.default}`
            }}>
              <h3 style={{ 
                fontSize: typography.fontSize.base,
                fontWeight: 600,
                color: colors.text.primary,
                marginBottom: spacing.md 
              }}>
                Data Refresh Status
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xs }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                  <span style={{ color: colors.accent.success }}>✓</span>
                  <span>Data Saved to PostgreSQL</span>
                </div>
                {result.dcs_score !== null && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                    <span style={{ color: colors.accent.success }}>✓</span>
                    <span>DCS Updated: {result.dcs_score.toFixed(1)}</span>
                  </div>
                )}
                {result.risk_score !== null && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                    <span style={{ color: colors.accent.success }}>✓</span>
                    <span>Risk Score Updated: {result.risk_score.toFixed(1)}</span>
                  </div>
                )}
                {result.anomaly_count !== null && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                    <span style={{ color: colors.accent.success }}>✓</span>
                    <span>Anomalies Detected: {result.anomaly_count}</span>
                  </div>
                )}
                {result.governance_status && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                    <span style={{ color: colors.accent.success }}>✓</span>
                    <span>Governance Status: {result.governance_status}</span>
                  </div>
                )}
                <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                  <span style={{ color: colors.accent.success }}>✓</span>
                  <span>Audit Event Recorded</span>
                </div>
              </div>
            </div>
            
            <Button
              variant="primary"
              onClick={() => {
                setSubmitted(false);
                setResult(null);
                setFormData({
                  project_id: '',
                  reporting_month: '',
                  revised_cost: '',
                  expenditure: '',
                  physical_progress: '',
                  planned_completion: '',
                  narrative_text: '',
                  revision_reason: '',
                });
              }}
              style={{ marginTop: spacing.lg }}
            >
              Submit Another
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      <Card padding="lg">
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(2, 1fr)', 
            gap: spacing.md 
          }}>
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: typography.fontSize.sm, 
                fontWeight: 600,
                color: colors.text.secondary,
                marginBottom: spacing.xs 
              }}>
                Project ID *
              </label>
              <input
                type="text"
                name="project_id"
                value={formData.project_id}
                onChange={handleChange}
                style={{
                  width: '100%',
                  padding: `${spacing.sm} ${spacing.md}`,
                  backgroundColor: colors.background.primary,
                  border: `1px solid ${validationErrors.project_id ? colors.accent.danger : colors.border.default}`,
                  borderRadius: borderRadius.md,
                  color: colors.text.primary,
                  fontFamily: typography.fontFamily.sans,
                  fontSize: typography.fontSize.sm,
                }}
                required
              />
              {validationErrors.project_id && (
                <div style={{ 
                  fontSize: typography.fontSize.xs, 
                  color: colors.accent.danger, 
                  marginTop: spacing.xs 
                }}>
                  {validationErrors.project_id}
                </div>
              )}
            </div>
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: typography.fontSize.sm, 
                fontWeight: 600,
                color: colors.text.secondary,
                marginBottom: spacing.xs 
              }}>
                Reporting Month *
              </label>
              <input
                type="month"
                name="reporting_month"
                value={formData.reporting_month}
                onChange={handleChange}
                style={{
                  width: '100%',
                  padding: `${spacing.sm} ${spacing.md}`,
                  backgroundColor: colors.background.primary,
                  border: `1px solid ${validationErrors.reporting_month ? colors.accent.danger : colors.border.default}`,
                  borderRadius: borderRadius.md,
                  color: colors.text.primary,
                  fontFamily: typography.fontFamily.sans,
                  fontSize: typography.fontSize.sm,
                }}
                required
              />
              {validationErrors.reporting_month && (
                <div style={{ 
                  fontSize: typography.fontSize.xs, 
                  color: colors.accent.danger, 
                  marginTop: spacing.xs 
                }}>
                  {validationErrors.reporting_month}
                </div>
              )}
            </div>
          </div>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(2, 1fr)', 
            gap: spacing.md 
          }}>
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: typography.fontSize.sm, 
                fontWeight: 600,
                color: colors.text.secondary,
                marginBottom: spacing.xs 
              }}>
                Revised Cost (₹ Crores)
              </label>
              <input
                type="number"
                name="revised_cost"
                value={formData.revised_cost}
                onChange={handleChange}
                style={{
                  width: '100%',
                  padding: `${spacing.sm} ${spacing.md}`,
                  backgroundColor: colors.background.primary,
                  border: `1px solid ${validationErrors.revised_cost ? colors.accent.danger : colors.border.default}`,
                  borderRadius: borderRadius.md,
                  color: colors.text.primary,
                  fontFamily: typography.fontFamily.sans,
                  fontSize: typography.fontSize.sm,
                }}
                min="0"
                step="0.01"
              />
              {validationErrors.revised_cost && (
                <div style={{ 
                  fontSize: typography.fontSize.xs, 
                  color: colors.accent.danger, 
                  marginTop: spacing.xs 
                }}>
                  {validationErrors.revised_cost}
                </div>
              )}
            </div>
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: typography.fontSize.sm, 
                fontWeight: 600,
                color: colors.text.secondary,
                marginBottom: spacing.xs 
              }}>
                Expenditure (₹ Crores)
              </label>
              <input
                type="number"
                name="expenditure"
                value={formData.expenditure}
                onChange={handleChange}
                style={{
                  width: '100%',
                  padding: `${spacing.sm} ${spacing.md}`,
                  backgroundColor: colors.background.primary,
                  border: `1px solid ${validationErrors.expenditure ? colors.accent.danger : colors.border.default}`,
                  borderRadius: borderRadius.md,
                  color: colors.text.primary,
                  fontFamily: typography.fontFamily.sans,
                  fontSize: typography.fontSize.sm,
                }}
                min="0"
                step="0.01"
              />
              {validationErrors.expenditure && (
                <div style={{ 
                  fontSize: typography.fontSize.xs, 
                  color: colors.accent.danger, 
                  marginTop: spacing.xs 
                }}>
                  {validationErrors.expenditure}
                </div>
              )}
            </div>
          </div>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(2, 1fr)', 
            gap: spacing.md 
          }}>
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: typography.fontSize.sm, 
                fontWeight: 600,
                color: colors.text.secondary,
                marginBottom: spacing.xs 
              }}>
                Physical Progress (%) *
              </label>
              <input
                type="number"
                name="physical_progress"
                value={formData.physical_progress}
                onChange={handleChange}
                style={{
                  width: '100%',
                  padding: `${spacing.sm} ${spacing.md}`,
                  backgroundColor: colors.background.primary,
                  border: `1px solid ${validationErrors.physical_progress ? colors.accent.danger : colors.border.default}`,
                  borderRadius: borderRadius.md,
                  color: colors.text.primary,
                  fontFamily: typography.fontFamily.sans,
                  fontSize: typography.fontSize.sm,
                }}
                required
                min="0"
                max="100"
                step="0.1"
              />
              {validationErrors.physical_progress && (
                <div style={{ 
                  fontSize: typography.fontSize.xs, 
                  color: colors.accent.danger, 
                  marginTop: spacing.xs 
                }}>
                  {validationErrors.physical_progress}
                </div>
              )}
            </div>
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: typography.fontSize.sm, 
                fontWeight: 600,
                color: colors.text.secondary,
                marginBottom: spacing.xs 
              }}>
                Planned Completion Date
              </label>
              <input
                type="date"
                name="planned_completion"
                value={formData.planned_completion}
                onChange={handleChange}
                style={{
                  width: '100%',
                  padding: `${spacing.sm} ${spacing.md}`,
                  backgroundColor: colors.background.primary,
                  border: `1px solid ${colors.border.default}`,
                  borderRadius: borderRadius.md,
                  color: colors.text.primary,
                  fontFamily: typography.fontFamily.sans,
                  fontSize: typography.fontSize.sm,
                }}
              />
            </div>
          </div>

          <div>
            <label style={{ 
              display: 'block', 
              fontSize: typography.fontSize.sm, 
              fontWeight: 600,
              color: colors.text.secondary,
              marginBottom: spacing.xs 
            }}>
              Narrative Remarks
            </label>
            <textarea
              name="narrative_text"
              value={formData.narrative_text}
              onChange={handleChange}
              style={{
                width: '100%',
                padding: `${spacing.sm} ${spacing.md}`,
                backgroundColor: colors.background.primary,
                border: `1px solid ${colors.border.default}`,
                borderRadius: borderRadius.md,
                color: colors.text.primary,
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.sm,
                minHeight: '100px',
              }}
              rows="4"
              placeholder="Provide any additional context or remarks..."
            />
          </div>

          <div style={{ 
            padding: spacing.md,
            backgroundColor: `${colors.accent.primary}10`,
            border: `1px solid ${colors.accent.primary}30`,
            borderRadius: borderRadius.md 
          }}>
            <h3 style={{ 
              fontWeight: 600,
              color: colors.accent.primary,
              marginBottom: spacing.sm 
            }}>
              Validation Rules
            </h3>
            <ul style={{ 
              fontSize: typography.fontSize.sm,
              color: colors.text.secondary,
              paddingLeft: spacing.md 
            }}>
              <li>• Physical progress must be between 0 and 100</li>
              <li>• Expenditure and revised cost cannot be negative</li>
              <li>• Duplicate reporting months will be rejected</li>
              <li>• Cost consistency will be checked against previous submissions</li>
            </ul>
          </div>

          <div style={{ 
            padding: spacing.md,
            backgroundColor: `${colors.accent.warning}10`,
            border: `1px solid ${colors.accent.warning}30`,
            borderRadius: borderRadius.md 
          }}>
            <h3 style={{ 
              fontWeight: 600,
              color: colors.accent.warning,
              marginBottom: spacing.sm 
            }}>
              Impact of Submission
            </h3>
            <ul style={{ 
              fontSize: typography.fontSize.sm,
              color: colors.text.secondary,
              paddingLeft: spacing.md 
            }}>
              <li>• DCS will be recalculated</li>
              <li>• Anomaly detection will be re-run</li>
              <li>• Risk score will be recalculated</li>
              <li>• Governance queue will be reassessed if risk crosses threshold</li>
            </ul>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: spacing.md }}>
            <Button
              variant="ghost"
              onClick={() => setFormData({
                project_id: '',
                reporting_month: '',
                revised_cost: '',
                expenditure: '',
                physical_progress: '',
                planned_completion: '',
                narrative_text: '',
                revision_reason: '',
              })}
            >
              Clear
            </Button>
            <Button variant="primary" type="submit" disabled={loading}>
              {loading ? 'Submitting...' : 'Submit'}
            </Button>
          </div>

          {error && (
            <div style={{ 
              padding: spacing.md,
              backgroundColor: `${colors.accent.danger}10`,
              border: `1px solid ${colors.accent.danger}30`,
              borderRadius: borderRadius.md,
              color: colors.accent.danger,
            }}>
              {error}
            </div>
          )}

          {/* Duplicate Dialog */}
          {showDuplicateDialog && (
            <div style={{ 
              padding: spacing.lg,
              backgroundColor: `${colors.accent.warning}10`,
              border: `2px solid ${colors.accent.warning}`,
              borderRadius: borderRadius.md,
              marginBottom: spacing.lg,
            }}>
              <h3 style={{ 
                fontSize: typography.fontSize.lg,
                fontWeight: 600,
                color: colors.accent.warning,
                marginBottom: spacing.md 
              }}>
                ⚠️ Duplicate Reporting Month
              </h3>
              <p style={{ 
                fontSize: typography.fontSize.sm,
                color: colors.text.secondary,
                marginBottom: spacing.lg 
              }}>
                A submission for {formData.reporting_month} already exists for this project.
                You can either revise the existing submission or cancel.
              </p>
              
              <div style={{ marginBottom: spacing.lg }}>
                <label style={{ 
                  display: 'block',
                  fontSize: typography.fontSize.sm,
                  fontWeight: 600,
                  color: colors.text.secondary,
                  marginBottom: spacing.xs 
                }}>
                  Revision Reason (Required) *
                </label>
                <textarea
                  name="revision_reason"
                  value={formData.revision_reason}
                  onChange={handleChange}
                  style={{
                    width: '100%',
                    padding: `${spacing.sm} ${spacing.md}`,
                    backgroundColor: colors.background.primary,
                    border: `1px solid ${colors.border.default}`,
                    borderRadius: borderRadius.md,
                    color: colors.text.primary,
                    fontFamily: typography.fontFamily.sans,
                    fontSize: typography.fontSize.sm,
                    minHeight: '80px',
                  }}
                  placeholder="Explain why this revision is necessary..."
                  rows="3"
                />
              </div>
              
              <div style={{ display: 'flex', gap: spacing.md }}>
                <Button
                  variant="primary"
                  onClick={handleRevise}
                  disabled={loading || !formData.revision_reason.trim()}
                >
                  {loading ? 'Revising...' : 'Revise Existing Submission'}
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => {
                    setShowDuplicateDialog(false);
                    setFormData(prev => ({ ...prev, revision_reason: '' }));
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </form>
      </Card>
    </div>
  );
}

export default DataEntry;
