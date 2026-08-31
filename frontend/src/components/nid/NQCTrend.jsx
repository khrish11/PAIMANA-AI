import { Card, EmptyState } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { memo } from 'react';

function NQCTrend({ historyData }) {
  if (!historyData || historyData.length === 0) {
    return (
      <Card padding="lg" role="region" aria-label="NQC Trend">
        <EmptyState icon="📈" title="No NQC History" description="Historical narrative-coherence observations are unavailable." />
      </Card>
    );
  }

  const getNQCColor = (score) => {
    if (score >= 80) return colors.accent.success;
    if (score >= 60) return colors.accent.warning;
    return colors.accent.danger;
  };

  return (
    <Card padding="lg" role="region" aria-label="NQC Trend">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        NQC Trend
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
        {historyData.map((point, index) => (
          <div 
            key={index}
            style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              padding: spacing.sm,
              backgroundColor: colors.background.tertiary,
              borderRadius: borderRadius.sm
            }}
          >
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              {point.date || point.month}
            </div>
            <div style={{ 
              fontSize: typography.fontSize.base, 
              fontWeight: 600, 
              color: getNQCColor(point.nqc_score) 
            }}>
              {point.nqc_score?.toFixed(0)}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

export default memo(NQCTrend);
