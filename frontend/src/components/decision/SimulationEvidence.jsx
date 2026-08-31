import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function SimulationEvidence({ result, scenarios }) {
  if (!result) {
    return null;
  }

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          SIMULATION EVIDENCE
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Model basis and input values used for the counterfactual analysis.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
        {/* Model Basis */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            MODEL BASIS
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
            <strong>Risk model:</strong> risk-model-v1_synthetic
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, marginTop: spacing.xs }}>
            Baseline and counterfactual states are evaluated using the same risk model for consistency.
          </div>
        </div>

        {/* Input Parameters */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            INPUT PARAMETERS
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
            The following parameters were used in the simulation:
          </div>
          <ul style={{ marginTop: spacing.sm, paddingLeft: spacing.lg, color: colors.text.secondary }}>
            <li>cost_overrun_ratio</li>
            <li>schedule_slip_months</li>
            <li>physical_progress</li>
          </ul>
        </div>

        {/* Applied Changes */}
        {scenarios && scenarios.length > 0 && (
          <div style={{ 
            padding: spacing.lg,
            backgroundColor: colors.background.tertiary,
            borderRadius: '0.5rem',
            border: `1px solid ${colors.border.light}`
          }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
              APPLIED CHANGES
            </div>
            {scenarios.filter(s => s.proposed_value !== s.current_value).map((scenario) => (
              <div key={scenario.parameter} style={{ marginBottom: spacing.sm }}>
                <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
                  <strong>{scenario.parameter}:</strong> {scenario.current_value} → {scenario.proposed_value}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Result Evidence */}
        {result.results && (
          <div style={{ 
            padding: spacing.lg,
            backgroundColor: colors.background.tertiary,
            borderRadius: '0.5rem',
            border: `1px solid ${colors.border.light}`
          }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
              RESULT EVIDENCE
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: spacing.md }}>
              <div>
                <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>
                  Baseline Risk
                </div>
                <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
                  {result.results.before_risk?.toFixed(1) || 'N/A'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>
                  Counterfactual Risk
                </div>
                <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
                  {result.results.after_risk?.toFixed(1) || 'N/A'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>
                  Baseline Cost
                </div>
                <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
                  {formatCurrency(result.results.before_cost)}
                </div>
              </div>
              <div>
                <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>
                  Counterfactual Cost
                </div>
                <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
                  {formatCurrency(result.results.after_cost)}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div style={{ 
        marginTop: spacing.lg,
        padding: spacing.md,
        backgroundColor: `${colors.accent.info}10`,
        borderRadius: '0.375rem',
        border: `1px solid ${colors.accent.info}30`,
        fontSize: typography.fontSize.sm,
        color: colors.text.secondary
      }}>
        <strong>Data Provenance:</strong> All simulation results are calculated by the backend counterfactual engine using the existing PAIMANA risk model. No values are fabricated or estimated on the frontend.
      </div>
    </Card>
  );
}
