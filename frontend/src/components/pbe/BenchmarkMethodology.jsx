import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';
import { memo } from 'react';

function BenchmarkMethodology() {
  return (
    <Card padding="lg" role="region" aria-label="Benchmark Methodology">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        HOW BENCHMARKING WORKS
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        <div style={{ display: 'flex', gap: spacing.sm }}>
          <div style={{ 
            width: '24px', 
            height: '24px', 
            borderRadius: '50%', 
            backgroundColor: colors.accent.primary, 
            color: colors.background.primary,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: typography.fontSize.sm,
            fontWeight: 600,
            flexShrink: 0
          }}>
            1
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
            Identify comparable projects by sector and size band
          </div>
        </div>

        <div style={{ display: 'flex', gap: spacing.sm }}>
          <div style={{ 
            width: '24px', 
            height: '24px', 
            borderRadius: '50%', 
            backgroundColor: colors.accent.primary, 
            color: colors.background.primary,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: typography.fontSize.sm,
            fontWeight: 600,
            flexShrink: 0
          }}>
            2
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
            Construct stage-aware peer cohort
          </div>
        </div>

        <div style={{ display: 'flex', gap: spacing.sm }}>
          <div style={{ 
            width: '24px', 
            height: '24px', 
            borderRadius: '50%', 
            backgroundColor: colors.accent.primary, 
            color: colors.background.primary,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: typography.fontSize.sm,
            fontWeight: 600,
            flexShrink: 0
          }}>
            3
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
            Calculate peer distribution (cost overrun, schedule slip)
          </div>
        </div>

        <div style={{ display: 'flex', gap: spacing.sm }}>
          <div style={{ 
            width: '24px', 
            height: '24px', 
            borderRadius: '50%', 
            backgroundColor: colors.accent.primary, 
            color: colors.background.primary,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: typography.fontSize.sm,
            fontWeight: 600,
            flexShrink: 0
          }}>
            4
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
            Position current project within distribution
          </div>
        </div>

        <div style={{ display: 'flex', gap: spacing.sm }}>
          <div style={{ 
            width: '24px', 
            height: '24px', 
            borderRadius: '50%', 
            backgroundColor: colors.accent.primary, 
            color: colors.background.primary,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: typography.fontSize.sm,
            fontWeight: 600,
            flexShrink: 0
          }}>
            5
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
            Compute percentile and PPI score
          </div>
        </div>

        <div style={{ display: 'flex', gap: spacing.sm }}>
          <div style={{ 
            width: '24px', 
            height: '24px', 
            borderRadius: '50%', 
            backgroundColor: colors.accent.primary, 
            color: colors.background.primary,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: typography.fontSize.sm,
            fontWeight: 600,
            flexShrink: 0
          }}>
            6
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
            Identify significant performance gaps
          </div>
        </div>
      </div>

      <div style={{ marginTop: spacing.lg, paddingTop: spacing.md, borderTop: `1px solid ${colors.border.default}`, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        Benchmark methodology is defined by the PBE service.
      </div>
    </Card>
  );
}

export default memo(BenchmarkMethodology);
