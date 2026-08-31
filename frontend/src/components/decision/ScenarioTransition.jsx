import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function ScenarioTransition({ result }) {
  if (!result || !result.results) {
    return null;
  }

  const { results } = result;

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(value);
  };

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
          SCENARIO TRANSITION
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Visual transition from baseline to counterfactual outcome.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
        {/* Baseline */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            BASELINE
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: spacing.md }}>
            <div>
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted, marginBottom: spacing.xs }}>
                Risk
              </div>
              <div style={{ fontSize: typography.fontSize.xl, fontWeight: 600, color: colors.text.primary }}>
                {results.before_risk !== null && results.before_risk !== undefined
                  ? results.before_risk.toFixed(1)
                  : 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted, marginBottom: spacing.xs }}>
                Cost
              </div>
              <div style={{ fontSize: typography.fontSize.xl, fontWeight: 600, color: colors.text.primary }}>
                {formatCurrency(results.before_cost)}
              </div>
            </div>
            <div>
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted, marginBottom: spacing.xs }}>
                Completion
              </div>
              <div style={{ fontSize: typography.fontSize.xl, fontWeight: 600, color: colors.text.primary }}>
                {results.before_completion_months !== null && results.before_completion_months !== undefined
                  ? `${results.before_completion_months.toFixed(0)} mo`
                  : 'N/A'}
              </div>
            </div>
          </div>
        </div>

        {/* Arrow */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center',
          color: colors.accent.primary,
          fontSize: typography.fontSize['2xl'],
          fontWeight: 700
        }}>
          ↓
        </div>

        {/* Scenario */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: `${colors.accent.primary}10`,
          borderRadius: '0.5rem',
          border: `2px solid ${colors.accent.primary}30`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.accent.primary, marginBottom: spacing.sm, fontWeight: 600 }}>
            SCENARIO
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: spacing.md }}>
            <div>
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted, marginBottom: spacing.xs }}>
                Risk
              </div>
              <div style={{ fontSize: typography.fontSize.xl, fontWeight: 700, color: colors.accent.primary }}>
                {results.after_risk !== null && results.after_risk !== undefined
                  ? results.after_risk.toFixed(1)
                  : 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted, marginBottom: spacing.xs }}>
                Cost
              </div>
              <div style={{ fontSize: typography.fontSize.xl, fontWeight: 700, color: colors.accent.primary }}>
                {formatCurrency(results.after_cost)}
              </div>
            </div>
            <div>
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted, marginBottom: spacing.xs }}>
                Completion
              </div>
              <div style={{ fontSize: typography.fontSize.xl, fontWeight: 700, color: colors.accent.primary }}>
                {results.after_completion_months !== null && results.after_completion_months !== undefined
                  ? `${results.after_completion_months.toFixed(0)} mo`
                  : 'N/A'}
              </div>
            </div>
          </div>
        </div>

        {/* Net Effect */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.secondary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            NET EFFECT
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: spacing.md }}>
            <div>
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted, marginBottom: spacing.xs }}>
                Risk
              </div>
              <div style={{ 
                fontSize: typography.fontSize.xl, 
                fontWeight: 700, 
                color: getDeltaColor(results.risk_delta) 
              }}>
                {results.risk_delta !== null && results.risk_delta !== undefined
                  ? `${getDeltaSign(results.risk_delta)}${results.risk_delta.toFixed(1)}`
                  : '-'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted, marginBottom: spacing.xs }}>
                Cost
              </div>
              <div style={{ 
                fontSize: typography.fontSize.xl, 
                fontWeight: 700, 
                color: getDeltaColor(results.cost_delta) 
              }}>
                {results.cost_delta !== null && results.cost_delta !== undefined
                  ? `${getDeltaSign(results.cost_delta)}${formatCurrency(results.cost_delta)}`
                  : '-'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted, marginBottom: spacing.xs }}>
                Schedule
              </div>
              <div style={{ 
                fontSize: typography.fontSize.xl, 
                fontWeight: 700, 
                color: getDeltaColor(results.schedule_delta) 
              }}>
                {results.schedule_delta !== null && results.schedule_delta !== undefined
                  ? `${getDeltaSign(results.schedule_delta)}${results.schedule_delta.toFixed(0)} mo`
                  : '-'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
