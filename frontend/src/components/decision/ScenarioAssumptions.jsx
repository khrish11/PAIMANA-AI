import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function ScenarioAssumptions() {
  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          SCENARIO ASSUMPTIONS
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Known assumptions underlying the counterfactual simulation.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        <div style={{ 
          padding: spacing.md,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.375rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            MODEL ASSUMPTION
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
            Baseline and counterfactual states are evaluated using the same risk model (risk-model-v1_synthetic) for consistency.
          </div>
        </div>

        <div style={{ 
          padding: spacing.md,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.375rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            MODEL ASSUMPTION
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
            Schedule estimation uses a simplified formula (36 months + schedule slip) rather than full RCF forecast integration.
          </div>
        </div>

        <div style={{ 
          padding: spacing.md,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.375rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            MODEL ASSUMPTION
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
            Counterfactual state is created in memory and does not modify actual project records.
          </div>
        </div>

        <div style={{ 
          padding: spacing.md,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.375rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            PROJECT FACT
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
            Baseline project data is loaded from actual project records and remains unchanged.
          </div>
        </div>

        <div style={{ 
          padding: spacing.md,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.375rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            MODEL ASSUMPTION
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
            Risk scoring uses the existing PAIMANA composite risk model with cost, schedule, progress, and governance components.
          </div>
        </div>
      </div>

      <div style={{ 
        marginTop: spacing.lg,
        padding: spacing.md,
        backgroundColor: colors.background.secondary,
        borderRadius: '0.375rem',
        border: `1px solid ${colors.border.light}`,
        fontSize: typography.fontSize.sm,
        color: colors.text.muted
      }}>
        <strong>Important:</strong> These assumptions are inherent to the current simulation model. Results should be interpreted within these constraints.
      </div>
    </Card>
  );
}
