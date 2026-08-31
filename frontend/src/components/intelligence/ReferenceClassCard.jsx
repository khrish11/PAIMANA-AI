import { Card, Badge } from '../common';
import { colors, spacing, typography, borderRadius, shadows } from '../../tokens';
import { memo } from 'react';

function ReferenceClassCard({ referenceData }) {
  if (!referenceData) {
    return (
      <Card padding="lg">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          Reference class intelligence unavailable
        </div>
      </Card>
    );
  }

  const getPercentileColor = (percentile) => {
    if (percentile >= 90) return colors.risk.critical;
    if (percentile >= 75) return colors.risk.high;
    if (percentile >= 50) return colors.risk.medium;
    return colors.risk.low;
  };

  return (
    <Card padding="lg">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Reference-Class Intelligence
      </h3>

      {/* Reference class metadata */}
      <div style={{ marginBottom: spacing.lg, padding: spacing.md, backgroundColor: colors.background.tertiary, borderRadius: borderRadius.md }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xs }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
            <span style={{ color: colors.text.muted }}>Sector:</span> {referenceData.sector || 'N/A'}
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
            <span style={{ color: colors.text.muted }}>Size Band:</span> {referenceData.size_band || 'N/A'}
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
            <span style={{ color: colors.text.muted }}>Region:</span> {referenceData.region || 'N/A'}
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
            <span style={{ color: colors.text.muted }}>Comparable Projects:</span> {referenceData.comparable_count || 'N/A'}
          </div>
        </div>
      </div>

      {/* Current project percentile */}
      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
          Current Project
        </div>
        <div style={{ fontSize: typography.fontSize['3xl'], fontWeight: 700, color: getPercentileColor(referenceData.current_percentile || 0) }}>
          {referenceData.current_percentile ? `${referenceData.current_percentile}th` : 'N/A'}
        </div>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
          percentile
        </div>
      </div>

      {/* Cohort statistics */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: spacing.sm, backgroundColor: colors.background.tertiary, borderRadius: borderRadius.sm }}>
          <span style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>Cohort Median</span>
          <span style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.primary }}>
            {referenceData.cohort_median ? `${referenceData.cohort_median}th` : 'N/A'}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: spacing.sm, backgroundColor: colors.background.tertiary, borderRadius: borderRadius.sm }}>
          <span style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>P75</span>
          <span style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.primary }}>
            {referenceData.p75 ? `${referenceData.p75}th` : 'N/A'}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: spacing.sm, backgroundColor: colors.background.tertiary, borderRadius: borderRadius.sm }}>
          <span style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>P90</span>
          <span style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.primary }}>
            {referenceData.p90 ? `${referenceData.p90}th` : 'N/A'}
          </span>
        </div>
      </div>

      {/* Interpretation badge */}
      {referenceData.current_percentile && (
        <div style={{ marginTop: spacing.lg }}>
          <Badge
            variant={referenceData.current_percentile >= 75 ? 'warning' : 'success'}
            size="md"
          >
            {referenceData.current_percentile >= 75 ? 'Above cohort average' : 'Within cohort range'}
          </Badge>
        </div>
      )}

      {/* Distribution Visualization */}
      {referenceData.current_percentile !== undefined && (
        <div style={{ marginTop: spacing.xl, paddingTop: spacing.lg, borderTop: `1px solid ${colors.border.default}` }}>
          <div style={{ marginBottom: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
            Cohort Distribution
          </div>
          
          <div style={{ position: 'relative', height: '60px', backgroundColor: colors.background.tertiary, borderRadius: borderRadius.md, padding: spacing.sm }}>
            {/* Distribution bars */}
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', height: '100%' }}>
              {/* P90 marker */}
              <div style={{ 
                position: 'relative', 
                height: '8px', 
                backgroundColor: colors.border.light, 
                borderRadius: borderRadius.sm 
              }}>
                <div style={{ 
                  position: 'absolute', 
                  left: `${referenceData.p90}%`, 
                  top: 0, 
                  width: '2px', 
                  height: '100%', 
                  backgroundColor: colors.accent.danger 
                }} />
                <div style={{ 
                  position: 'absolute', 
                  left: `${referenceData.p90}%`, 
                  top: '100%', 
                  transform: 'translateX(-50%)', 
                  fontSize: typography.fontSize.xs, 
                  color: colors.text.muted,
                  marginTop: spacing.xs
                }}>
                  P90
                </div>
              </div>
              
              {/* P75 marker */}
              <div style={{ 
                position: 'relative', 
                height: '8px', 
                backgroundColor: colors.border.light, 
                borderRadius: borderRadius.sm 
              }}>
                <div style={{ 
                  position: 'absolute', 
                  left: `${referenceData.p75}%`, 
                  top: 0, 
                  width: '2px', 
                  height: '100%', 
                  backgroundColor: colors.accent.warning 
                }} />
                <div style={{ 
                  position: 'absolute', 
                  left: `${referenceData.p75}%`, 
                  top: '100%', 
                  transform: 'translateX(-50%)', 
                  fontSize: typography.fontSize.xs, 
                  color: colors.text.muted,
                  marginTop: spacing.xs
                }}>
                  P75
                </div>
              </div>
              
              {/* Median marker */}
              <div style={{ 
                position: 'relative', 
                height: '8px', 
                backgroundColor: colors.border.light, 
                borderRadius: borderRadius.sm 
              }}>
                <div style={{ 
                  position: 'absolute', 
                  left: `${referenceData.cohort_median}%`, 
                  top: 0, 
                  width: '2px', 
                  height: '100%', 
                  backgroundColor: colors.accent.primary 
                }} />
                <div style={{ 
                  position: 'absolute', 
                  left: `${referenceData.cohort_median}%`, 
                  top: '100%', 
                  transform: 'translateX(-50%)', 
                  fontSize: typography.fontSize.xs, 
                  color: colors.text.muted,
                  marginTop: spacing.xs
                }}>
                  Median
                </div>
              </div>
              
              {/* Current project marker */}
              <div style={{ 
                position: 'relative', 
                height: '12px', 
                backgroundColor: `${colors.accent.primary}20`, 
                borderRadius: borderRadius.sm 
              }}>
                <div style={{ 
                  position: 'absolute', 
                  left: `${referenceData.current_percentile}%`, 
                  top: '-50%', 
                  transform: 'translateX(-50%)', 
                  width: '24px', 
                  height: '24px', 
                  borderRadius: '50%', 
                  backgroundColor: colors.accent.primary, 
                  border: '3px solid white',
                  boxShadow: shadows.sm
                }} />
                <div style={{ 
                  position: 'absolute', 
                  left: `${referenceData.current_percentile}%`, 
                  top: '100%', 
                  transform: 'translateX(-50%)', 
                  fontSize: typography.fontSize.xs, 
                  fontWeight: 600, 
                  color: colors.text.primary,
                  marginTop: spacing.xs
                }}>
                  You are here
                </div>
              </div>
            </div>
          </div>
          
          <div style={{ marginTop: spacing.sm, fontSize: typography.fontSize.xs, color: colors.text.muted, textAlign: 'center' }}>
            0% ───────────────────────────────────────────────────────────── 100%
          </div>
        </div>
      )}
    </Card>
  );
}

export default memo(ReferenceClassCard);
