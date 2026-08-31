import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function CurrentState({ baseline }) {
  if (!baseline) {
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
          BASELINE PROJECT STATE
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Current project metrics from actual project data.
        </p>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: spacing.lg 
      }}>
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            RISK
          </div>
          <div style={{ 
            fontSize: typography.fontSize['3xl'], 
            fontWeight: 700, 
            color: colors.text.primary 
          }}>
            {baseline.risk_score !== null && baseline.risk_score !== undefined 
              ? baseline.risk_score.toFixed(1) 
              : 'N/A'}
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginTop: spacing.xs }}>
            Risk Score
          </div>
        </div>

        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            COST
          </div>
          <div style={{ 
            fontSize: typography.fontSize['2xl'], 
            fontWeight: 700, 
            color: colors.text.primary 
          }}>
            {formatCurrency(baseline.revised_cost)}
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginTop: spacing.xs }}>
            Revised Cost
          </div>
        </div>

        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            COMPLETION
          </div>
          <div style={{ 
            fontSize: typography.fontSize['2xl'], 
            fontWeight: 700, 
            color: colors.text.primary 
          }}>
            {baseline.completion_months !== null && baseline.completion_months !== undefined
              ? `${baseline.completion_months.toFixed(0)} mo`
              : 'N/A'}
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginTop: spacing.xs }}>
            Projected Duration
          </div>
        </div>

        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            PHYSICAL PROGRESS
          </div>
          <div style={{ 
            fontSize: typography.fontSize['2xl'], 
            fontWeight: 700, 
            color: colors.text.primary 
          }}>
            {baseline.physical_progress !== null && baseline.physical_progress !== undefined
              ? `${baseline.physical_progress.toFixed(1)}%`
              : 'N/A'}
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginTop: spacing.xs }}>
            Progress to Date
          </div>
        </div>
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
        <strong>Data Source:</strong> Project records loaded from backend. These values represent the actual current state of the project.
      </div>
    </Card>
  );
}
