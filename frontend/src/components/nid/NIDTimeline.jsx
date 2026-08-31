import { Card, EmptyState, Badge } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { memo } from 'react';

function NIDTimeline({ events }) {
  if (!events || events.length === 0) {
    return (
      <Card padding="lg" role="region" aria-label="NID Timeline">
        <EmptyState icon="📅" title="No NID Events" description="No NID events recorded for this project." />
      </Card>
    );
  }

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
    <Card padding="lg" role="region" aria-label="NID Timeline">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        NID Timeline
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        {events.map((event, index) => (
          <div 
            key={index}
            style={{ 
              display: 'flex', 
              gap: spacing.md,
              padding: spacing.md,
              backgroundColor: colors.background.tertiary,
              borderRadius: borderRadius.md,
              borderLeft: `3px solid ${getSeverityColor(event.severity) || colors.border.default}`
            }}
          >
            <div style={{ minWidth: '80px', fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              {event.date}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary, marginBottom: spacing.xs }}>
                {event.event}
              </div>
              <div style={{ display: 'flex', gap: spacing.sm, alignItems: 'center' }}>
                {event.severity && (
                  <Badge
                    variant={event.severity === 'CRITICAL' ? 'critical' : event.severity === 'HIGH' ? 'danger' : event.severity === 'MODERATE' ? 'warning' : 'info'}
                    size="sm"
                  >
                    {event.severity}
                  </Badge>
                )}
                {event.status && (
                  <span style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
                    {event.status}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

export default memo(NIDTimeline);
