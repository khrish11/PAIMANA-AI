import { Card, Badge } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { memo } from 'react';

function PeerGapAnalysis({ pbeData }) {
  if (!pbeData) {
    return (
      <Card padding="lg" role="region" aria-label="Peer Gap Analysis">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          Gap analysis unavailable
        </div>
      </Card>
    );
  }

  const gaps = [];

  if (pbeData.peer_relative_cost_variance > 0.05) {
    gaps.push({
      metric: 'COST',
      delta: `+${(pbeData.peer_relative_cost_variance * 100).toFixed(1)}% above peer median`,
      severity: 'HIGH',
    });
  } else if (pbeData.peer_relative_cost_variance < -0.05) {
    gaps.push({
      metric: 'COST',
      delta: `${(pbeData.peer_relative_cost_variance * 100).toFixed(1)}% below peer median`,
      severity: 'LOW',
    });
  }

  if (pbeData.peer_relative_schedule_variance > 3) {
    gaps.push({
      metric: 'SCHEDULE',
      delta: `+${pbeData.peer_relative_schedule_variance.toFixed(1)} months worse than peer median`,
      severity: 'HIGH',
    });
  } else if (pbeData.peer_relative_schedule_variance < -3) {
    gaps.push({
      metric: 'SCHEDULE',
      delta: `${pbeData.peer_relative_schedule_variance.toFixed(1)} months better than peer median`,
      severity: 'LOW',
    });
  }

  if (pbeData.peer_reporting_quality < 70) {
    gaps.push({
      metric: 'REPORTING QUALITY',
      delta: `${pbeData.peer_reporting_quality.toFixed(0)} - Below peer average`,
      severity: 'MODERATE',
    });
  }

  if (gaps.length === 0) {
    return (
      <Card padding="lg" role="region" aria-label="Peer Gap Analysis">
        <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
          WHERE IS THE PROJECT UNDERPERFORMING?
        </h3>
        <div style={{ textAlign: 'center', color: colors.text.secondary, padding: spacing.lg }}>
          Project performance is broadly consistent with comparable peers.
        </div>
      </Card>
    );
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'HIGH': return colors.accent.danger;
      case 'MODERATE': return colors.accent.warning;
      case 'LOW': return colors.accent.info;
      default: return colors.text.muted;
    }
  };

  return (
    <Card padding="lg" role="region" aria-label="Peer Gap Analysis">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        WHERE IS THE PROJECT UNDERPERFORMING?
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        {gaps.map((gap, index) => (
          <div 
            key={index}
            style={{ 
              padding: spacing.md, 
              backgroundColor: colors.background.tertiary, 
              borderRadius: borderRadius.md,
              borderLeft: `4px solid ${getSeverityColor(gap.severity)}`
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.xs }}>
              <span style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
                {gap.metric}
              </span>
              <Badge
                variant={gap.severity === 'HIGH' ? 'danger' : gap.severity === 'MODERATE' ? 'warning' : 'info'}
                size="sm"
              >
                {gap.severity}
              </Badge>
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              {gap.delta}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

export default memo(PeerGapAnalysis);
