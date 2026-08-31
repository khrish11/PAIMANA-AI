import { Card } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { memo } from 'react';

function PeerPosition({ pbeData }) {
  if (!pbeData) {
    return (
      <Card padding="lg" role="region" aria-label="Peer Position">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          Peer position unavailable
        </div>
      </Card>
    );
  }

  if (pbeData.cohort_size === 0) {
    return (
      <Card padding="lg" role="region" aria-label="Peer Position">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          INSUFFICIENT PEER DATA
        </div>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, marginTop: spacing.sm }}>
          Too few comparable projects are available for a reliable benchmark.
        </div>
      </Card>
    );
  }

  const getPercentileColor = (percentile) => {
    if (percentile >= 80) return colors.accent.success;
    if (percentile >= 60) return colors.accent.warning;
    return colors.accent.danger;
  };

  const positionPercent = pbeData.percentile;

  return (
    <Card padding="lg" role="region" aria-label="Peer Position">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        WHERE DO I STAND?
      </h3>

      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
          LOW PERFORMANCE ───────────────────────────────────────────────────────────── HIGH PERFORMANCE
        </div>
        <div style={{ position: 'relative', height: '40px', backgroundColor: colors.background.tertiary, borderRadius: borderRadius.md }}>
          <div 
            style={{ 
              position: 'absolute',
              left: `${positionPercent}%`,
              top: '50%',
              transform: 'translate(-50%, -50%)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}
          >
            <div style={{ 
              width: '0', 
              height: '0', 
              borderLeft: '8px solid transparent',
              borderRight: '8px solid transparent',
              borderBottom: `12px solid ${getPercentileColor(positionPercent)}` 
            }} />
            <div style={{ 
              fontSize: typography.fontSize.sm, 
              fontWeight: 600, 
              color: getPercentileColor(positionPercent),
              marginTop: spacing.xs
            }}>
              THIS PROJECT
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: spacing.lg }}>
        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            PROJECT
          </div>
          <div style={{ fontSize: typography.fontSize['3xl'], fontWeight: 700, color: getPercentileColor(positionPercent) }}>
            {positionPercent.toFixed(0)}th percentile
          </div>
        </div>

        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            PEER MEDIAN
          </div>
          <div style={{ fontSize: typography.fontSize['3xl'], fontWeight: 700, color: colors.text.primary }}>
            50th percentile
          </div>
        </div>
      </div>

      <div style={{ marginTop: spacing.lg, paddingTop: spacing.md, borderTop: `1px solid ${colors.border.default}` }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
          {pbeData.explanation || 'Project performance compared to peer cohort.'}
        </div>
      </div>
    </Card>
  );
}

export default memo(PeerPosition);
