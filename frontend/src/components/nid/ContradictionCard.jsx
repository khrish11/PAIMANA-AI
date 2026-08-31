import { Card, Badge, Button } from '../common';
import { colors, spacing, typography, borderRadius, shadows } from '../../tokens';
import { memo } from 'react';

function ContradictionCard({ contradiction, onInvestigate }) {
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

  const getSeverityVariant = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'critical';
      case 'HIGH': return 'danger';
      case 'MODERATE': return 'warning';
      case 'LOW': return 'info';
      default: return 'default';
    }
  };

  return (
    <Card 
      padding="lg" 
      role="region" 
      aria-label={`Contradiction: ${contradiction.severity}`}
      style={{ 
        borderLeft: `4px solid ${getSeverityColor(contradiction.severity)}`,
        transition: 'all 150ms ease-in-out'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = shadows.md;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: spacing.md }}>
        <Badge
          variant={getSeverityVariant(contradiction.severity)}
          size="md"
          aria-label={`Severity: ${contradiction.severity}`}
        >
          {contradiction.severity}
        </Badge>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => onInvestigate?.(contradiction)}
          aria-label="View evidence for this contradiction"
        >
          Investigate
        </Button>
      </div>

      <div style={{ marginBottom: spacing.md }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
          NARRATIVE CLAIM
        </div>
        <div style={{ 
          fontSize: typography.fontSize.base, 
          color: colors.text.primary,
          fontStyle: 'italic',
          padding: spacing.sm,
          backgroundColor: colors.background.tertiary,
          borderRadius: borderRadius.sm
        }}>
          &ldquo;{contradiction.claim}&rdquo;
        </div>
      </div>

      <div style={{ marginBottom: spacing.md }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
          QUANTITATIVE EVIDENCE
        </div>
        <div style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          {contradiction.referenced_cuf_field}: {contradiction.actual_value}
        </div>
      </div>

      <div style={{ marginBottom: spacing.md }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
          NID INTERPRETATION
        </div>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
          {contradiction.explanation}
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: spacing.md, borderTop: `1px solid ${colors.border.default}` }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
          Coherence: {contradiction.coherence_score?.toFixed(2) || 'N/A'}
        </div>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
          Field: {contradiction.referenced_cuf_field}
        </div>
      </div>
    </Card>
  );
}

export default memo(ContradictionCard);
