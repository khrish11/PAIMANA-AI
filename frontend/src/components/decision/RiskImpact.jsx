import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function RiskImpact({ result }) {
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

  const getInterpretation = (delta) => {
    if (delta === null || delta === undefined) return 'No change in risk.';
    if (delta < 0) return `Risk decreased by ${Math.abs(delta).toFixed(1)} points under this scenario.`;
    if (delta > 0) return `Risk increased by ${delta.toFixed(1)} points under this scenario.`;
    return 'No change in risk.';
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
          RISK IMPACT
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Projected change in risk score under the counterfactual scenario.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: spacing.lg }}>
        {/* Baseline Risk */}
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            BASELINE RISK
          </div>
          <div style={{ 
            fontSize: typography.fontSize['4xl'], 
            fontWeight: 700, 
            color: colors.text.primary 
          }}>
            {results.before_risk !== null && results.before_risk !== undefined
              ? results.before_risk.toFixed(1)
              : 'N/A'}
          </div>
        </div>

        {/* Arrow */}
        <div style={{ 
          fontSize: typography.fontSize['3xl'],
          color: colors.accent.primary,
          fontWeight: 700
        }}>
          ↓
        </div>

        {/* Scenario Risk */}
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.accent.primary, marginBottom: spacing.sm, fontWeight: 600 }}>
            SCENARIO RISK
          </div>
          <div style={{ 
            fontSize: typography.fontSize['4xl'], 
            fontWeight: 700, 
            color: colors.accent.primary 
          }}>
            {results.after_risk !== null && results.after_risk !== undefined
              ? results.after_risk.toFixed(1)
              : 'N/A'}
          </div>
        </div>

        {/* Delta */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`,
          textAlign: 'center',
          width: '100%'
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            CHANGE
          </div>
          <div style={{ 
            fontSize: typography.fontSize['2xl'], 
            fontWeight: 700, 
            color: getDeltaColor(results.risk_delta) 
          }}>
            {results.risk_delta !== null && results.risk_delta !== undefined
              ? `${getDeltaSign(results.risk_delta)}${results.risk_delta.toFixed(1)} points`
              : '-'}
          </div>
        </div>

        {/* Interpretation */}
        <div style={{ 
          padding: spacing.md,
          backgroundColor: `${colors.accent.info}10`,
          borderRadius: '0.375rem',
          border: `1px solid ${colors.accent.info}30`,
          fontSize: typography.fontSize.base,
          color: colors.text.secondary,
          textAlign: 'center',
          width: '100%'
        }}>
          {getInterpretation(results.risk_delta)}
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
        <strong>Model Basis:</strong> Risk calculated using the existing PAIMANA risk model (risk-model-v1_synthetic). Under this scenario, the model projects the risk change shown above.
      </div>
    </Card>
  );
}
