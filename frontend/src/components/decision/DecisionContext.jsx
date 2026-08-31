import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function DecisionContext({ baseline, result }) {
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
          DECISION CONTEXT
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Summary of current project state and scenario projections for decision support.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
        {/* Current Project Risk */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            CURRENT PROJECT RISK
          </div>
          <div style={{ 
            fontSize: typography.fontSize['3xl'], 
            fontWeight: 700, 
            color: colors.text.primary 
          }}>
            {baseline?.risk_score !== null && baseline?.risk_score !== undefined
              ? baseline.risk_score.toFixed(1)
              : 'N/A'}
          </div>
        </div>

        {/* Scenario Risk */}
        {result?.results && (
          <div style={{ 
            padding: spacing.lg,
            backgroundColor: `${colors.accent.primary}10`,
            borderRadius: '0.5rem',
            border: `2px solid ${colors.accent.primary}30`
          }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.accent.primary, marginBottom: spacing.sm, fontWeight: 600 }}>
              SCENARIO RISK
            </div>
            <div style={{ 
              fontSize: typography.fontSize['3xl'], 
              fontWeight: 700, 
              color: colors.accent.primary 
            }}>
              {result.results.after_risk?.toFixed(1) || 'N/A'}
            </div>
          </div>
        )}

        {/* Projected Changes */}
        {result?.results && (
          <div style={{ 
            padding: spacing.lg,
            backgroundColor: colors.background.secondary,
            borderRadius: '0.5rem',
            border: `1px solid ${colors.border.light}`
          }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.md }}>
              PROJECTED CHANGES
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: spacing.md }}>
              <div>
                <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>
                  Cost Change
                </div>
                <div style={{ fontSize: typography.fontSize.lg, color: colors.text.primary, fontWeight: 600 }}>
                  {result.results.cost_delta !== null && result.results.cost_delta !== undefined
                    ? `${result.results.cost_delta > 0 ? '+' : ''}${formatCurrency(result.results.cost_delta)}`
                    : '-'}
                </div>
              </div>
              <div>
                <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>
                  Schedule Change
                </div>
                <div style={{ fontSize: typography.fontSize.lg, color: colors.text.primary, fontWeight: 600 }}>
                  {result.results.schedule_delta !== null && result.results.schedule_delta !== undefined
                    ? `${result.results.schedule_delta > 0 ? '+' : ''}${result.results.schedule_delta.toFixed(0)} mo`
                    : '-'}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div style={{ 
        marginTop: spacing.lg,
        padding: spacing.lg,
        backgroundColor: `${colors.accent.info}10`,
        borderRadius: '0.5rem',
        border: `1px solid ${colors.accent.info}30`,
        fontSize: typography.fontSize.base,
        color: colors.text.secondary,
        textAlign: 'center'
      }}>
        Use this simulation as decision support alongside project evidence, governance requirements, and operational judgement.
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
        <strong>Disclaimer:</strong> This simulation provides model-projected outcomes based on specified parameter changes. It does not replace comprehensive project analysis or governance review.
      </div>
    </Card>
  );
}
