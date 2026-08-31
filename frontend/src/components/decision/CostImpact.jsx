import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function CostImpact({ result }) {
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

  const getPercentageChange = (before, after) => {
    if (before === null || before === undefined || before === 0) return null;
    if (after === null || after === undefined) return null;
    return ((after - before) / before) * 100;
  };

  const percentageChange = getPercentageChange(results.before_cost, results.after_cost);

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          COST IMPACT
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Model-projected cost change under the counterfactual scenario.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
        {/* Baseline Cost */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            BASELINE COST
          </div>
          <div style={{ 
            fontSize: typography.fontSize['3xl'], 
            fontWeight: 700, 
            color: colors.text.primary 
          }}>
            {formatCurrency(results.before_cost)}
          </div>
        </div>

        {/* Scenario Cost */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: `${colors.accent.primary}10`,
          borderRadius: '0.5rem',
          border: `2px solid ${colors.accent.primary}30`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.accent.primary, marginBottom: spacing.sm, fontWeight: 600 }}>
            SCENARIO COST
          </div>
          <div style={{ 
            fontSize: typography.fontSize['3xl'], 
            fontWeight: 700, 
            color: colors.accent.primary 
          }}>
            {formatCurrency(results.after_cost)}
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
            color: getDeltaColor(results.cost_delta) 
          }}>
            {results.cost_delta !== null && results.cost_delta !== undefined
              ? `${getDeltaSign(results.cost_delta)}${formatCurrency(results.cost_delta)}`
              : '-'}
          </div>
          {percentageChange !== null && (
            <div style={{ 
              fontSize: typography.fontSize.sm, 
              color: colors.text.muted,
              marginTop: spacing.xs 
            }}>
              ({getDeltaSign(percentageChange)}{percentageChange.toFixed(1)}%)
            </div>
          )}
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
        <strong>MODEL-PROJECTED COST</strong>
        <br />
        This value is calculated by the simulation model based on the proposed cost overrun ratio. It does not represent actual expenditure or guaranteed project cost.
      </div>
    </Card>
  );
}
