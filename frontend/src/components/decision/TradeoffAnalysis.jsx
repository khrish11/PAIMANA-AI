import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function TradeoffAnalysis({ result }) {
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

  const getDirection = (delta) => {
    if (delta === null || delta === undefined) return '→';
    if (delta < 0) return '↓';
    if (delta > 0) return '↑';
    return '→';
  };

  const generateSummary = () => {
    const improvements = [];
    const worsenings = [];

    if (results.risk_delta < 0) {
      improvements.push('lower risk');
    } else if (results.risk_delta > 0) {
      worsenings.push('higher risk');
    }

    if (results.cost_delta < 0) {
      improvements.push('lower projected cost');
    } else if (results.cost_delta > 0) {
      worsenings.push('higher projected cost');
    }

    if (results.schedule_delta < 0) {
      improvements.push('shorter completion time');
    } else if (results.schedule_delta > 0) {
      worsenings.push('longer completion time');
    }

    if (improvements.length === 0 && worsenings.length === 0) {
      return 'Scenario projects no significant change in risk, cost, or schedule.';
    }

    let summary = 'Scenario projects ';
    
    if (improvements.length > 0) {
      summary += improvements.join(', ');
    }

    if (improvements.length > 0 && worsenings.length > 0) {
      summary += ', with ';
    }

    if (worsenings.length > 0) {
      summary += worsenings.join(', ');
    }

    summary += '.';

    return summary;
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
          TRADE-OFF ANALYSIS
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Summary of projected changes across risk, cost, and schedule dimensions.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: spacing.lg, marginBottom: spacing.lg }}>
        {/* Risk */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`,
          textAlign: 'center'
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            RISK
          </div>
          <div style={{ 
            fontSize: typography.fontSize['2xl'], 
            fontWeight: 700, 
            color: getDeltaColor(results.risk_delta),
            marginBottom: spacing.xs
          }}>
            {getDirection(results.risk_delta)}
          </div>
          <div style={{ fontSize: typography.fontSize.lg, color: colors.text.primary }}>
            {results.risk_delta !== null && results.risk_delta !== undefined
              ? `${getDeltaSign(results.risk_delta)}${Math.abs(results.risk_delta).toFixed(1)}`
              : '-'}
          </div>
        </div>

        {/* Cost */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`,
          textAlign: 'center'
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            COST
          </div>
          <div style={{ 
            fontSize: typography.fontSize['2xl'], 
            fontWeight: 700, 
            color: getDeltaColor(results.cost_delta),
            marginBottom: spacing.xs
          }}>
            {getDirection(results.cost_delta)}
          </div>
          <div style={{ fontSize: typography.fontSize.lg, color: colors.text.primary }}>
            {results.cost_delta !== null && results.cost_delta !== undefined
              ? `${getDeltaSign(results.cost_delta)}${formatCurrency(results.cost_delta)}`
              : '-'}
          </div>
        </div>

        {/* Schedule */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`,
          textAlign: 'center'
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            SCHEDULE
          </div>
          <div style={{ 
            fontSize: typography.fontSize['2xl'], 
            fontWeight: 700, 
            color: getDeltaColor(results.schedule_delta),
            marginBottom: spacing.xs
          }}>
            {getDirection(results.schedule_delta)}
          </div>
          <div style={{ fontSize: typography.fontSize.lg, color: colors.text.primary }}>
            {results.schedule_delta !== null && results.schedule_delta !== undefined
              ? `${getDeltaSign(results.schedule_delta)}${Math.abs(results.schedule_delta).toFixed(0)} mo`
              : '-'}
          </div>
        </div>
      </div>

      <div style={{ 
        padding: spacing.lg,
        backgroundColor: `${colors.accent.info}10`,
        borderRadius: '0.5rem',
        border: `1px solid ${colors.accent.info}30`,
        fontSize: typography.fontSize.base,
        color: colors.text.secondary,
        textAlign: 'center'
      }}>
        {generateSummary()}
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
        <strong>Note:</strong> This analysis is based on model-projected changes. Use this simulation as decision support alongside project evidence, governance requirements, and operational judgement.
      </div>
    </Card>
  );
}
