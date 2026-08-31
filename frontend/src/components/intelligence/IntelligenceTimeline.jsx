import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function IntelligenceTimeline({ intelligence }) {
  const { data } = intelligence;

  const trend = data.trend;

  if (!trend || !trend.trend || trend.trend.length === 0) {
    return (
      <Card padding="lg">
        <div style={{ marginBottom: spacing.lg }}>
          <h2 style={{ 
            fontSize: typography.fontSize['2xl'], 
            fontWeight: 700, 
            color: colors.text.primary,
            marginBottom: spacing.xs 
          }}>
            INTELLIGENCE TIMELINE
          </h2>
          <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
            Temporal view of intelligence metrics.
          </p>
        </div>
        <div style={{ 
          padding: spacing.xl,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          textAlign: 'center',
          color: colors.text.muted
        }}>
          Historical trend data not available.
        </div>
      </Card>
    );
  }

  const getRiskColor = (score) => {
    if (score >= 75) return colors.accent.danger;
    if (score >= 60) return colors.accent.danger;
    if (score >= 45) return colors.accent.warning;
    if (score >= 30) return colors.accent.info;
    return colors.accent.success;
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
          INTELLIGENCE TIMELINE
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Temporal view of intelligence metrics over time.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        {/* Timeline Header */}
        <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr 1fr 1fr', gap: spacing.sm, padding: spacing.sm, backgroundColor: colors.background.secondary, borderRadius: '0.375rem', fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.muted }}>
          <div>Month</div>
          <div>Risk</div>
          <div>Cost Risk</div>
          <div>Schedule Risk</div>
        </div>

        {/* Timeline Items */}
        {trend.trend.map((point, index) => (
          <div key={index} style={{ 
            display: 'grid', 
            gridTemplateColumns: '120px 1fr 1fr 1fr', 
            gap: spacing.sm, 
            padding: spacing.md,
            backgroundColor: colors.background.tertiary,
            borderRadius: '0.375rem',
            border: `1px solid ${colors.border.light}`
          }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              {point.reporting_month}
            </div>
            <div style={{ 
              fontSize: typography.fontSize.base, 
              fontWeight: 600, 
              color: getRiskColor(point.composite_score) 
            }}>
              {point.composite_score.toFixed(1)}
            </div>
            <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
              {point.cost_risk?.toFixed(1) || 'N/A'}
            </div>
            <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
              {point.schedule_risk?.toFixed(1) || 'N/A'}
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div style={{ marginTop: spacing.lg, display: 'flex', gap: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: colors.accent.success, borderRadius: '2px' }}></div>
          <span>LOW</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: colors.accent.info, borderRadius: '2px' }}></div>
          <span>MODERATE</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: colors.accent.warning, borderRadius: '2px' }}></div>
          <span>HIGH</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: colors.accent.danger, borderRadius: '2px' }}></div>
          <span>CRITICAL</span>
        </div>
      </div>

      <div style={{ marginTop: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>SOURCE:</strong> Risk Trend API (synthetic demo data)
      </div>
    </Card>
  );
}
