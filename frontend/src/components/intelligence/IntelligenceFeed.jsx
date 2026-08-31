import { Card, Badge, Button } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';

function IntelligenceFeed({ events, onProjectClick }) {
  if (!events || events.length === 0) {
    return (
      <Card padding="lg">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          No recent intelligence events
        </div>
      </Card>
    );
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return colors.accent.critical;
      case 'HIGH': return colors.accent.danger;
      case 'WARNING': return colors.accent.warning;
      case 'DATA': return colors.accent.info;
      case 'NETWORK': return colors.accent.secondary;
      default: return colors.text.muted;
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'CRITICAL': return '🔴';
      case 'HIGH': return '🟠';
      case 'WARNING': return '🟡';
      case 'DATA': return '🟢';
      case 'NETWORK': return '🔵';
      default: return '⚪';
    }
  };

  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return 'N/A';
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now - then;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <Card padding="lg">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Intelligence Feed
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        {events.slice(0, 10).map((event, index) => (
          <div
            key={index}
            style={{
              padding: spacing.md,
              backgroundColor: colors.background.tertiary,
              borderRadius: borderRadius.md,
              borderLeft: `3px solid ${getSeverityColor(event.severity)}`,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: spacing.sm }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                <span>{getSeverityIcon(event.severity)}</span>
                <Badge
                  variant={
                    event.severity === 'CRITICAL' ? 'critical' :
                    event.severity === 'HIGH' ? 'danger' :
                    event.severity === 'WARNING' ? 'warning' : 'info'
                  }
                  size="sm"
                >
                  {event.severity}
                </Badge>
              </div>
              <span style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>
                {formatTimeAgo(event.timestamp)}
              </span>
            </div>

            <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
              {event.event_type}
            </div>

            {event.project_name && (
              <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
                {event.project_name}
              </div>
            )}

            {event.explanation && (
              <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
                {event.explanation}
              </div>
            )}

            {event.risk_change && (
              <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
                Risk: {event.previous_risk?.toFixed(1)} → {event.current_risk?.toFixed(1)} 
                <span style={{ color: event.risk_change >= 0 ? colors.accent.danger : colors.accent.success, fontWeight: 600 }}>
                  {event.risk_change >= 0 ? '+' : ''}{event.risk_change.toFixed(1)}
                </span>
              </div>
            )}

            {event.primary_driver && (
              <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
                Primary driver: {event.primary_driver}
              </div>
            )}

            {event.project_id && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onProjectClick?.(event.project_id)}
                style={{ marginTop: spacing.xs }}
              >
                Investigate
              </Button>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
}

export default IntelligenceFeed;
