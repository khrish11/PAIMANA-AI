import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function ScheduleImpact({ result }) {
  if (!result || !result.results) {
    return null;
  }

  const { results } = result;

  const getDeltaColor = (delta) => {
    if (delta === null || delta === undefined) return colors.text.muted;
    if (delta < 0) return colors.accent.success;
    if (delta > 0) return colors.accent.danger;
    return colors.text.muted;
  };

  const getDeltaSign = (delta) => {
    if (delta === null || delta === undefined) return '';
    if (delta > 0) return '+';
    return '';
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
          SCHEDULE IMPACT
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Model-projected completion time change under the counterfactual scenario.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
        {/* Baseline Completion */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            BASELINE COMPLETION
          </div>
          <div style={{ 
            fontSize: typography.fontSize['3xl'], 
            fontWeight: 700, 
            color: colors.text.primary 
          }}>
            {results.before_completion_months !== null && results.before_completion_months !== undefined
              ? `${results.before_completion_months.toFixed(0)} months`
              : 'N/A'}
          </div>
        </div>

        {/* Scenario Completion */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: `${colors.accent.primary}10`,
          borderRadius: '0.5rem',
          border: `2px solid ${colors.accent.primary}30`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.accent.primary, marginBottom: spacing.sm, fontWeight: 600 }}>
            SCENARIO COMPLETION
          </div>
          <div style={{ 
            fontSize: typography.fontSize['3xl'], 
            fontWeight: 700, 
            color: colors.accent.primary 
          }}>
            {results.after_completion_months !== null && results.after_completion_months !== undefined
              ? `${results.after_completion_months.toFixed(0)} months`
              : 'N/A'}
          </div>
        </div>

        {/* Delta */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.secondary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            DELTA
          </div>
          <div style={{ 
            fontSize: typography.fontSize['2xl'], 
            fontWeight: 700, 
            color: getDeltaColor(results.schedule_delta) 
          }}>
            {results.schedule_delta !== null && results.schedule_delta !== undefined
              ? `${getDeltaSign(results.schedule_delta)}${results.schedule_delta.toFixed(0)} months`
              : '-'}
          </div>
        </div>
      </div>

      <div style={{ 
        marginTop: spacing.lg,
        padding: spacing.md,
        backgroundColor: `${colors.accent.warning}10`,
        borderRadius: '0.375rem',
        border: `1px solid ${colors.accent.warning}30`,
        fontSize: typography.fontSize.sm,
        color: colors.text.secondary
      }}>
        <strong>MODEL-PROJECTED COMPLETION</strong>
        <br />
        This value is calculated by the simulation model using a simplified formula (36 months + schedule slip). It does not represent a guaranteed completion date.
      </div>
    </Card>
  );
}
