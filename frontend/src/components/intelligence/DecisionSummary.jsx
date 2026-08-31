import { Card, Badge } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function DecisionSummary({ intelligence }) {
  const { data } = intelligence;

  const getRiskCategory = (score) => {
    if (score === null || score === undefined) return 'N/A';
    if (score >= 75) return 'CRITICAL';
    if (score >= 60) return 'VERY_HIGH';
    if (score >= 45) return 'HIGH';
    if (score >= 30) return 'MODERATE';
    return 'LOW';
  };

  const getRiskBadgeVariant = (category) => {
    switch (category) {
      case 'CRITICAL': return 'critical';
      case 'VERY_HIGH': return 'danger';
      case 'HIGH': return 'warning';
      case 'MODERATE': return 'info';
      default: return 'success';
    }
  };

  const risk = data.risk;
  const rcf = data.rcf;
  const pbe = data.pbe;
  const dcs = risk?.dcs;

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          EXECUTIVE DECISION SUMMARY
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Key intelligence metrics at a glance.
        </p>
      </div>

      {/* Four Key Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: spacing.lg, marginBottom: spacing.xl }}>
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
            fontSize: typography.fontSize['3xl'], 
            fontWeight: 700, 
            color: colors.text.primary,
            marginBottom: spacing.xs
          }}>
            {risk?.composite_score !== null && risk?.composite_score !== undefined
              ? risk.composite_score.toFixed(1)
              : 'N/A'}
          </div>
          {risk && (
            <Badge variant={getRiskBadgeVariant(getRiskCategory(risk.composite_score))} size="sm">
              {getRiskCategory(risk.composite_score)}
            </Badge>
          )}
        </div>

        {/* Forecast */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`,
          textAlign: 'center'
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            FORECAST
          </div>
          <div style={{ 
            fontSize: typography.fontSize['3xl'], 
            fontWeight: 700, 
            color: colors.text.primary,
            marginBottom: spacing.xs
          }}>
            {rcf?.p80_completion_months !== null && rcf?.p80_completion_months !== undefined
              ? `${rcf.p80_completion_months.toFixed(0)}mo`
              : 'N/A'}
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
            P80 completion
          </div>
        </div>

        {/* Peer Position */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`,
          textAlign: 'center'
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            PEER POSITION
          </div>
          <div style={{ 
            fontSize: typography.fontSize['3xl'], 
            fontWeight: 700, 
            color: colors.text.primary,
            marginBottom: spacing.xs
          }}>
            {pbe?.percentile !== null && pbe?.percentile !== undefined
              ? `${pbe.percentile.toFixed(0)}%`
              : 'N/A'}
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
            percentile
          </div>
        </div>

        {/* Data Confidence */}
        <div style={{ 
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`,
          textAlign: 'center'
        }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            DATA CONFIDENCE
          </div>
          <div style={{ 
            fontSize: typography.fontSize['3xl'], 
            fontWeight: 700, 
            color: colors.text.primary,
            marginBottom: spacing.xs
          }}>
            {dcs?.dcs_score !== null && dcs?.dcs_score !== undefined
              ? dcs.dcs_score.toFixed(0)
              : 'N/A'}
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
            DCS score
          </div>
        </div>
      </div>

      {/* Key Signals */}
      <div style={{ 
        padding: spacing.lg,
        backgroundColor: colors.background.secondary,
        borderRadius: '0.5rem',
        border: `1px solid ${colors.border.light}`
      }}>
        <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.md }}>
          KEY SIGNALS
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
          {/* Risk Signal */}
          {risk && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: colors.text.secondary }}>Risk</span>
              <span style={{ fontWeight: 600, color: colors.text.primary }}>
                {getRiskCategory(risk.composite_score)}
              </span>
            </div>
          )}
          
          {/* Peer Signal */}
          {pbe && pbe.percentile !== null && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: colors.text.secondary }}>Peer</span>
              <span style={{ fontWeight: 600, color: colors.text.primary }}>
                {pbe.percentile > 50 ? 'Worse than' : 'Better than'} {Math.abs(100 - pbe.percentile).toFixed(0)}% of comparable projects
              </span>
            </div>
          )}
          
          {/* Forecast Signal */}
          {rcf && rcf.p80_completion_months !== null && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: colors.text.secondary }}>Forecast</span>
              <span style={{ fontWeight: 600, color: colors.text.primary }}>
                P80 completion: {rcf.p80_completion_months.toFixed(0)} months
              </span>
            </div>
          )}
          
          {/* Data Signal */}
          {dcs && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: colors.text.secondary }}>Data</span>
              <span style={{ fontWeight: 600, color: colors.text.primary }}>
                {dcs.dcs_score.toFixed(0)}% confidence / {dcs.confidence_label}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Source Labels */}
      <div style={{ marginTop: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>SOURCE:</strong> Risk Model, Reference Class Forecast, Peer Benchmark Engine, Data Confidence Score
      </div>
    </Card>
  );
}
