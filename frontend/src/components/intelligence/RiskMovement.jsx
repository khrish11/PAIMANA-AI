import { Card, Badge, Button } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';

function RiskMovement({ movements, onInvestigate }) {
  if (!movements || movements.length === 0) {
    return (
      <Card padding="lg">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          No recent risk movements
        </div>
      </Card>
    );
  }

  const getMovementColor = (change) => {
    if (change > 10) return colors.accent.critical;
    if (change > 5) return colors.accent.danger;
    if (change > 0) return colors.accent.warning;
    if (change < -10) return colors.accent.success;
    return colors.text.secondary;
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
        Risk Movement
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        {movements.slice(0, 8).map((movement, index) => (
          <div
            key={index}
            style={{
              padding: spacing.md,
              backgroundColor: colors.background.tertiary,
              borderRadius: borderRadius.md,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.xs }}>
                <Badge
                  variant={movement.change > 0 ? 'danger' : 'success'}
                  size="sm"
                >
                  {movement.change > 0 ? 'RISK INCREASED' : 'RISK DECREASED'}
                </Badge>
                <span style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>
                  {formatTimeAgo(movement.timestamp)}
                </span>
              </div>

              <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.xs }}>
                {movement.project_name}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                <span style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
                  {movement.previous_risk?.toFixed(1)} → {movement.current_risk?.toFixed(1)}
                </span>
                <span
                  style={{
                    fontSize: typography.fontSize.sm,
                    fontWeight: 600,
                    color: getMovementColor(movement.change),
                  }}
                >
                  {movement.change > 0 ? '+' : ''}{movement.change?.toFixed(1)}
                </span>
              </div>

              {movement.primary_driver && (
                <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginTop: spacing.xs }}>
                  Primary driver: {movement.primary_driver}
                </div>
              )}
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => onInvestigate?.(movement.project_id)}
              style={{ marginLeft: spacing.md }}
            >
              Investigate
            </Button>
          </div>
        ))}
      </div>
    </Card>
  );
}

export default RiskMovement;
