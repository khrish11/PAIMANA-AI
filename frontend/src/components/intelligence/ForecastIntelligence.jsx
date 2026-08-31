import { Card, EmptyState } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { memo } from 'react';

function ForecastIntelligence({ forecastData }) {
  if (!forecastData) {
    return (
      <Card padding="lg">
        <EmptyState icon="📊" title="Forecast Unavailable" description="Forecast intelligence is unavailable for this project." />
      </Card>
    );
  }

  const costForecast = forecastData.cost_forecast;
  const completionForecast = forecastData.completion_forecast;

  const renderForecastBar = (label, baseline, p50, p80, p90, unit = '') => {
    const maxValue = Math.max(baseline, p50, p80, p90) * 1.1;
    const baselinePercent = (baseline / maxValue) * 100;
    const p50Percent = (p50 / maxValue) * 100;
    const p80Percent = (p80 / maxValue) * 100;
    const p90Percent = (p90 / maxValue) * 100;

    return (
      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ marginBottom: spacing.md, fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
          {label}
        </div>
        
        <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
          Baseline: {baseline?.toFixed(0) || 'N/A'}{unit}
        </div>
        
        <div style={{ position: 'relative', height: '40px', backgroundColor: colors.background.tertiary, borderRadius: borderRadius.md, overflow: 'hidden' }}>
          {/* Baseline */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              width: `${baselinePercent}%`,
              height: '100%',
              backgroundColor: colors.border.light,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              paddingRight: spacing.xs,
              fontSize: typography.fontSize.xs,
              color: colors.text.muted,
            }}
          >
            {baseline?.toFixed(0)}
          </div>
          
          {/* P50 */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              width: `${p50Percent}%`,
              height: '100%',
              backgroundColor: `${colors.accent.success}40`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              paddingRight: spacing.xs,
              fontSize: typography.fontSize.xs,
              color: colors.text.primary,
              fontWeight: 600,
            }}
          >
            P50: {p50?.toFixed(0)}
          </div>
          
          {/* P80 */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              width: `${p80Percent}%`,
              height: '100%',
              backgroundColor: `${colors.accent.warning}40`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              paddingRight: spacing.xs,
              fontSize: typography.fontSize.xs,
              color: colors.text.primary,
              fontWeight: 600,
            }}
          >
            P80: {p80?.toFixed(0)}
          </div>
          
          {/* P90 */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              width: `${p90Percent}%`,
              height: '100%',
              backgroundColor: `${colors.accent.danger}40`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              paddingRight: spacing.xs,
              fontSize: typography.fontSize.xs,
              color: colors.text.primary,
              fontWeight: 600,
            }}
          >
            P90: {p90?.toFixed(0)}
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: spacing.lg, marginTop: spacing.sm, fontSize: typography.fontSize.xs, color: colors.text.muted }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
            <div style={{ width: '12px', height: '12px', backgroundColor: `${colors.accent.success}40`, borderRadius: borderRadius.sm }} />
            <span>P50</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
            <div style={{ width: '12px', height: '12px', backgroundColor: `${colors.accent.warning}40`, borderRadius: borderRadius.sm }} />
            <span>P80</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
            <div style={{ width: '12px', height: '12px', backgroundColor: `${colors.accent.danger}40`, borderRadius: borderRadius.sm }} />
            <span>P90</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <Card padding="lg">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Forecast Intelligence
      </h3>

      {/* Cost Forecast */}
      {costForecast && (
        <div style={{ marginBottom: spacing.xl }}>
          {renderForecastBar(
            'Final Cost Forecast',
            costForecast.current_baseline,
            costForecast.p50,
            costForecast.p80,
            costForecast.p90,
            ' Cr'
          )}
          
          {costForecast.variance !== undefined && (
            <div style={{ marginTop: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              Forecast Variance: {costForecast.variance >= 0 ? '+' : ''}{costForecast.variance.toFixed(1)}%
            </div>
          )}
        </div>
      )}

      {/* Completion Date Forecast */}
      {completionForecast && (
        <div>
          {renderForecastBar(
            'Completion Date Forecast',
            36, // Baseline in months
            parseFloat(completionForecast.p50) || 36,
            parseFloat(completionForecast.p80) || 36,
            parseFloat(completionForecast.p90) || 36,
            ' months'
          )}
          
          {completionForecast.delay_months !== undefined && (
            <div style={{ marginTop: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              Expected Delay: {completionForecast.delay_months} months
            </div>
          )}
        </div>
      )}

      {/* Reference Class Comparison */}
      {forecastData.reference_class_comparison && (
        <div style={{ marginTop: spacing.xl, paddingTop: spacing.lg, borderTop: `1px solid ${colors.border.default}` }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
            Reference-Class Comparison
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
            {forecastData.reference_class_comparison}
          </div>
        </div>
      )}
    </Card>
  );
}

export default memo(ForecastIntelligence);
