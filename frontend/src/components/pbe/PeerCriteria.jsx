import { Card } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { memo } from 'react';

function PeerCriteria({ pbeData }) {
  if (!pbeData) {
    return (
      <Card padding="lg" role="region" aria-label="Peer Criteria">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          Peer criteria unavailable
        </div>
      </Card>
    );
  }

  return (
    <Card padding="lg" role="region" aria-label="Peer Criteria">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        WHY THESE PEERS?
      </h3>

      <div style={{ marginBottom: spacing.md }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
          Comparable projects selected using:
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: spacing.md }}>
        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            SECTOR
          </div>
          <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
            {pbeData.cohort_sector || 'N/A'}
          </div>
        </div>

        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            PROJECT SIZE
          </div>
          <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
            {pbeData.cohort_size_band || 'N/A'}
          </div>
        </div>

        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            COMPARABLE PEERS
          </div>
          <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
            {pbeData.cohort_size || 0}
          </div>
        </div>

        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            STAGE NORMALISED
          </div>
          <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
            {pbeData.stage_normalised ? 'Yes' : 'No'}
          </div>
        </div>
      </div>

      {pbeData.cohort_size === 0 && (
        <div style={{ 
          marginTop: spacing.lg, 
          padding: spacing.md, 
          backgroundColor: `${colors.accent.warning}10`, 
          borderRadius: borderRadius.md,
          fontSize: typography.fontSize.sm,
          color: colors.text.secondary
        }}>
          ⚠️ No peers found in the same sector and size band for comparison.
        </div>
      )}
    </Card>
  );
}

export default memo(PeerCriteria);
