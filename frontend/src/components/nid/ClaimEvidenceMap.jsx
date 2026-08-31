import { Card, Badge } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { memo } from 'react';

function ClaimEvidenceMap({ contradiction }) {
  if (!contradiction) return null;

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return colors.accent.critical;
      case 'HIGH': return colors.accent.danger;
      case 'MODERATE': return colors.accent.warning;
      case 'LOW': return colors.accent.info;
      default: return colors.text.muted;
    }
  };

  return (
    <Card padding="lg" role="region" aria-label="Claim to Evidence Mapping">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Claim → Evidence Mapping
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            CLAIM
          </div>
          <div style={{ 
            fontSize: typography.fontSize.base, 
            color: colors.text.primary,
            padding: spacing.sm,
            backgroundColor: colors.background.tertiary,
            borderRadius: borderRadius.sm,
            fontStyle: 'italic'
          }}>
            &ldquo;{contradiction.claim}&rdquo;
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', color: colors.text.muted }}>
          ↓
        </div>

        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            QUANTITATIVE FIELD
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
            {contradiction.referenced_cuf_field}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', color: colors.text.muted }}>
          ↓
        </div>

        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            OBSERVED VALUE
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
            {contradiction.actual_value}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', color: colors.text.muted }}>
          ↓
        </div>

        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            EXPECTED VALUE (from narrative)
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
            {contradiction.expected_value}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', color: colors.text.muted }}>
          ↓
        </div>

        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            NID RESULT
          </div>
          <Badge
            variant={contradiction.severity === 'CRITICAL' ? 'critical' : contradiction.severity === 'HIGH' ? 'danger' : contradiction.severity === 'MODERATE' ? 'warning' : 'info'}
            size="md"
            style={{ backgroundColor: `${getSeverityColor(contradiction.severity)}20`, color: getSeverityColor(contradiction.severity) }}
          >
            INCONSISTENT
          </Badge>
        </div>

        <div style={{ marginTop: spacing.md, paddingTop: spacing.md, borderTop: `1px solid ${colors.border.default}` }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            COHERENCE SCORE
          </div>
          <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: getSeverityColor(contradiction.severity) }}>
            {contradiction.coherence_score?.toFixed(2) || 'N/A'}
          </div>
        </div>
      </div>
    </Card>
  );
}

export default memo(ClaimEvidenceMap);
