import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function WhatChanged({ intelligence }) {
  const { data } = intelligence;

  const trend = data.trend;

  // Get previous and current values from trend data
  const getChange = (trendData, field) => {
    if (!trendData || !trendData.trend || trendData.trend.length < 2) return null;
    
    const current = trendData.trend[trendData.trend.length - 1];
    const previous = trendData.trend[trendData.trend.length - 2];
    
    const currentValue = current[field];
    const previousValue = previous[field];
    
    if (currentValue === null || previousValue === null) return null;
    
    const delta = currentValue - previousValue;
    const direction = delta > 0 ? 'increased' : delta < 0 ? 'decreased' : 'unchanged';
    
    return {
      current: currentValue,
      previous: previousValue,
      delta,
      direction,
      currentMonth: current.reporting_month,
      previousMonth: previous.reporting_month
    };
  };

  const riskChange = getChange(trend, 'composite_score');
  const dcsChange = getChange(trend, 'dcs_score');

  const getDeltaColor = (delta) => {
    if (delta === null || delta === undefined) return colors.text.muted;
    if (delta > 0) return colors.accent.danger;
    if (delta < 0) return colors.accent.success;
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
          WHAT CHANGED?
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Comparison of previous state vs current state.
        </p>
      </div>

      {!trend || !trend.trend || trend.trend.length < 2 ? (
        <div style={{ 
          padding: spacing.xl,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          textAlign: 'center',
          color: colors.text.muted
        }}>
          Insufficient historical data to show changes.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
          {/* Risk Change */}
          {riskChange && (
            <div style={{ 
              padding: spacing.lg,
              backgroundColor: colors.background.tertiary,
              borderRadius: '0.5rem',
              border: `1px solid ${colors.border.light}`
            }}>
              <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.md }}>
                Risk
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: spacing.md }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                    {riskChange.previousMonth}
                  </div>
                  <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
                    {riskChange.previous.toFixed(1)}
                  </div>
                </div>
                <div style={{ 
                  fontSize: typography.fontSize['2xl'],
                  color: colors.accent.primary,
                  fontWeight: 700
                }}>
                  →
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                    {riskChange.currentMonth}
                  </div>
                  <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
                    {riskChange.current.toFixed(1)}
                  </div>
                </div>
                <div style={{ textAlign: 'center', minWidth: '100px' }}>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                    Change
                  </div>
                  <div style={{ 
                    fontSize: typography.fontSize['2xl'], 
                    fontWeight: 700, 
                    color: getDeltaColor(riskChange.delta) 
                  }}>
                    {getDeltaSign(riskChange.delta)}{riskChange.delta.toFixed(1)}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Data Confidence Change */}
          {dcsChange && (
            <div style={{ 
              padding: spacing.lg,
              backgroundColor: colors.background.tertiary,
              borderRadius: '0.5rem',
              border: `1px solid ${colors.border.light}`
            }}>
              <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.md }}>
                Data Confidence
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: spacing.md }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                    {dcsChange.previousMonth}
                  </div>
                  <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
                    {dcsChange.previous.toFixed(0)}%
                  </div>
                </div>
                <div style={{ 
                  fontSize: typography.fontSize['2xl'],
                  color: colors.accent.primary,
                  fontWeight: 700
                }}>
                  →
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                    {dcsChange.currentMonth}
                  </div>
                  <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
                    {dcsChange.current.toFixed(0)}%
                  </div>
                </div>
                <div style={{ textAlign: 'center', minWidth: '100px' }}>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                    Change
                  </div>
                  <div style={{ 
                    fontSize: typography.fontSize['2xl'], 
                    fontWeight: 700, 
                    color: getDeltaColor(dcsChange.delta) 
                  }}>
                    {getDeltaSign(dcsChange.delta)}{dcsChange.delta.toFixed(0)}%
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div style={{ marginTop: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>SOURCE:</strong> Risk Trend API (synthetic demo data)
      </div>
    </Card>
  );
}
