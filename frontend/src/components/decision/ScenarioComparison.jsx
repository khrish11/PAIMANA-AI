import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function ScenarioComparison({ result }) {
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
          BASELINE VS SCENARIO
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Comparison of current project state against simulated counterfactual outcome.
        </p>
      </div>

      <table style={{ 
        width: '100%',
        borderCollapse: 'collapse'
      }}>
        <thead>
          <tr style={{ borderBottom: `2px solid ${colors.border.light}` }}>
            <th style={{ 
              textAlign: 'left', 
              padding: spacing.md,
              fontSize: typography.fontSize.sm,
              color: colors.text.muted,
              fontWeight: 600
            }}>
              Metric
            </th>
            <th style={{ 
              textAlign: 'right', 
              padding: spacing.md,
              fontSize: typography.fontSize.sm,
              color: colors.text.muted,
              fontWeight: 600
            }}>
              Baseline
            </th>
            <th style={{ 
              textAlign: 'right', 
              padding: spacing.md,
              fontSize: typography.fontSize.sm,
              color: colors.text.muted,
              fontWeight: 600
            }}>
              Scenario
            </th>
            <th style={{ 
              textAlign: 'right', 
              padding: spacing.md,
              fontSize: typography.fontSize.sm,
              color: colors.text.muted,
              fontWeight: 600
            }}>
              Change
            </th>
          </tr>
        </thead>
        <tbody>
          <tr style={{ borderBottom: `1px solid ${colors.border.light}` }}>
            <td style={{ padding: spacing.lg, color: colors.text.primary, fontWeight: 600 }}>
              Risk Score
            </td>
            <td style={{ 
              padding: spacing.lg, 
              textAlign: 'right',
              color: colors.text.secondary 
            }}>
              {results.before_risk !== null && results.before_risk !== undefined
                ? results.before_risk.toFixed(1)
                : 'N/A'}
            </td>
            <td style={{ 
              padding: spacing.lg, 
              textAlign: 'right',
              color: colors.accent.primary,
              fontWeight: 600
            }}>
              {results.after_risk !== null && results.after_risk !== undefined
                ? results.after_risk.toFixed(1)
                : 'N/A'}
            </td>
            <td style={{ 
              padding: spacing.lg, 
              textAlign: 'right',
              color: getDeltaColor(results.risk_delta),
              fontWeight: 600
            }}>
              {results.risk_delta !== null && results.risk_delta !== undefined
                ? `${getDeltaSign(results.risk_delta)}${results.risk_delta.toFixed(1)}`
                : '-'}
            </td>
          </tr>

          <tr style={{ borderBottom: `1px solid ${colors.border.light}` }}>
            <td style={{ padding: spacing.lg, color: colors.text.primary, fontWeight: 600 }}>
              Cost
            </td>
            <td style={{ 
              padding: spacing.lg, 
              textAlign: 'right',
              color: colors.text.secondary 
            }}>
              {formatCurrency(results.before_cost)}
            </td>
            <td style={{ 
              padding: spacing.lg, 
              textAlign: 'right',
              color: colors.accent.primary,
              fontWeight: 600
            }}>
              {formatCurrency(results.after_cost)}
            </td>
            <td style={{ 
              padding: spacing.lg, 
              textAlign: 'right',
              color: getDeltaColor(results.cost_delta),
              fontWeight: 600
            }}>
              {results.cost_delta !== null && results.cost_delta !== undefined
                ? `${getDeltaSign(results.cost_delta)}${formatCurrency(results.cost_delta)}`
                : '-'}
            </td>
          </tr>

          <tr style={{ borderBottom: `1px solid ${colors.border.light}` }}>
            <td style={{ padding: spacing.lg, color: colors.text.primary, fontWeight: 600 }}>
              Completion
            </td>
            <td style={{ 
              padding: spacing.lg, 
              textAlign: 'right',
              color: colors.text.secondary 
            }}>
              {results.before_completion_months !== null && results.before_completion_months !== undefined
                ? `${results.before_completion_months.toFixed(0)} mo`
                : 'N/A'}
            </td>
            <td style={{ 
              padding: spacing.lg, 
              textAlign: 'right',
              color: colors.accent.primary,
              fontWeight: 600
            }}>
              {results.after_completion_months !== null && results.after_completion_months !== undefined
                ? `${results.after_completion_months.toFixed(0)} mo`
                : 'N/A'}
            </td>
            <td style={{ 
              padding: spacing.lg, 
              textAlign: 'right',
              color: getDeltaColor(results.schedule_delta),
              fontWeight: 600
            }}>
              {results.schedule_delta !== null && results.schedule_delta !== undefined
                ? `${getDeltaSign(results.schedule_delta)}${results.schedule_delta.toFixed(0)} mo`
                : '-'}
            </td>
          </tr>
        </tbody>
      </table>

      <div style={{ 
        marginTop: spacing.lg,
        padding: spacing.md,
        backgroundColor: `${colors.accent.info}10`,
        borderRadius: '0.375rem',
        border: `1px solid ${colors.accent.info}30`,
        fontSize: typography.fontSize.sm,
        color: colors.text.secondary
      }}>
        <strong>Data Source:</strong> Simulation results from backend counterfactual engine. Baseline values from actual project data. Scenario values are model-projected outcomes.
      </div>
    </Card>
  );
}
