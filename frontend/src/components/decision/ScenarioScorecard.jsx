import { Card, Badge } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function ScenarioScorecard({ result }) {
  if (!result || !result.results) {
    return null;
  }

  const { results } = result;

  const getMetricStatus = (delta) => {
    if (delta === null || delta === undefined) return { status: 'unchanged', label: 'Unchanged', variant: 'info' };
    if (delta < 0) return { status: 'improved', label: 'Improved', variant: 'success' };
    if (delta > 0) return { status: 'worsened', label: 'Worsened', variant: 'danger' };
    return { status: 'unchanged', label: 'Unchanged', variant: 'info' };
  };

  const riskStatus = getMetricStatus(results.risk_delta);
  const costStatus = getMetricStatus(results.cost_delta);
  const scheduleStatus = getMetricStatus(results.schedule_delta);

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          SCENARIO SCORECARD
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Summary of metric changes under the counterfactual scenario.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        {/* Risk */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div>
            <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
              Risk
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
              {results.risk_delta !== null && results.risk_delta !== undefined
                ? `${results.risk_delta > 0 ? '+' : ''}${results.risk_delta.toFixed(1)} points`
                : 'No change'}
            </div>
          </div>
          <Badge variant={riskStatus.variant} size="md">
            {riskStatus.label}
          </Badge>
        </div>

        {/* Cost */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div>
            <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
              Cost
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
              {results.cost_delta !== null && results.cost_delta !== undefined
                ? `${results.cost_delta > 0 ? '+' : ''}${new Intl.NumberFormat('en-IN', {
                    style: 'currency',
                    currency: 'INR',
                    maximumFractionDigits: 0,
                  }).format(results.cost_delta)}`
                : 'No change'}
            </div>
          </div>
          <Badge variant={costStatus.variant} size="md">
            {costStatus.label}
          </Badge>
        </div>

        {/* Schedule */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div>
            <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
              Schedule
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
              {results.schedule_delta !== null && results.schedule_delta !== undefined
                ? `${results.schedule_delta > 0 ? '+' : ''}${results.schedule_delta.toFixed(0)} months`
                : 'No change'}
            </div>
          </div>
          <Badge variant={scheduleStatus.variant} size="md">
            {scheduleStatus.label}
          </Badge>
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
        <strong>Interpretation:</strong> Lower risk, lower cost, and shorter completion time are considered improvements. Higher values indicate worsening under this scenario.
      </div>
    </Card>
  );
}
