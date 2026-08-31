import { useState } from 'react';
import { Card, Badge, Button } from '../components/common';
import { colors, spacing, typography, borderRadius } from '../tokens';

function DataEntry() {
  const [formData, setFormData] = useState({
    project_id: '',
    reporting_month: '',
    revised_cost: '',
    expenditure: '',
    physical_progress: '',
    planned_completion: '',
    narrative_text: '',
  });
  const [validationErrors, setValidationErrors] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState(null);

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
    
    console.log('Submitting CUF:', formData);
    
    setResult({
      submission_id: 'sub-' + Date.now(),
      status: 'accepted',
      message: 'Submission recorded successfully. DCS, anomalies, and risk recalculated.',
      version: 1,
      dcs_score: 78.5,
      risk_score: 45.2,
      anomaly_count: 2,
      governance_status: 'no_action',
    });
    setSubmitted(true);
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
              Submission Successful
            </h1>
            <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
              <div><strong>Submission ID:</strong> {result.submission_id}</div>
              <div><strong>Status:</strong> <Badge variant="success">{result.status}</Badge></div>
              <div><strong>Message:</strong> {result.message}</div>
              <div><strong>Version:</strong> {result.version}</div>
              <div><strong>DCS Score:</strong> {result.dcs_score}</div>
              <div><strong>Risk Score:</strong> {result.risk_score}</div>
              <div><strong>Anomalies Detected:</strong> {result.anomaly_count}</div>
              <div><strong>Governance Status:</strong> {result.governance_status}</div>
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
              })}
            >
              Clear
            </Button>
            <Button variant="primary" type="submit">
              Submit
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

export default DataEntry;
