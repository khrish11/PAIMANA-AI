import { Card, Badge } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { memo } from 'react';

function ProjectTimeline({ milestones, currentStage }) {
  if (!milestones || milestones.length === 0) {
    return (
      <Card padding="lg" role="region" aria-label="Project timeline">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          Project timeline unavailable
        </div>
      </Card>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return colors.accent.success;
      case 'in_progress': return colors.accent.primary;
      case 'pending': return colors.text.muted;
      case 'delayed': return colors.accent.warning;
      case 'blocked': return colors.accent.danger;
      default: return colors.text.muted;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return '✓';
      case 'in_progress': return '●';
      case 'pending': return '○';
      case 'delayed': return '⚠';
      case 'blocked': return '✕';
      default: return '○';
    }
  };

  return (
    <Card padding="lg" role="region" aria-label="Project timeline">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Project Timeline
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        {milestones.map((milestone, index) => {
          const isCurrent = milestone.stage === currentStage;
          
          return (
            <div
              key={index}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: spacing.md,
                padding: spacing.md,
                backgroundColor: isCurrent ? `${colors.accent.primary}10` : colors.background.tertiary,
                borderRadius: borderRadius.md,
                border: isCurrent ? `2px solid ${colors.accent.primary}` : '1px solid transparent',
                position: 'relative',
              }}
              role="listitem"
              aria-current={isCurrent ? 'step' : undefined}
            >
              {/* Status Icon */}
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                backgroundColor: getStatusColor(milestone.status),
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: colors.background.primary,
                fontSize: typography.fontSize.sm,
                fontWeight: 600,
                flexShrink: 0,
                'aria-hidden': true,
              }}>
                {getStatusIcon(milestone.status)}
              </div>

              {/* Milestone Details */}
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.xs }}>
                  <span style={{ 
                    fontSize: typography.fontSize.base, 
                    fontWeight: 600, 
                    color: colors.text.primary 
                  }}>
                    {milestone.name}
                  </span>
                  {isCurrent && (
                    <Badge variant="primary" size="sm" aria-label="Current stage">
                      Current Stage
                    </Badge>
                  )}
                </div>

                <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, marginBottom: spacing.xs }}>
                  {milestone.description || ''}
                </div>

                <div style={{ display: 'flex', gap: spacing.lg, fontSize: typography.fontSize.sm }}>
                  {milestone.date && (
                    <div style={{ color: colors.text.secondary }}>
                      <span style={{ color: colors.text.muted }}>Date:</span> {milestone.date}
                    </div>
                  )}
                  
                  {milestone.delay !== undefined && milestone.delay > 0 && (
                    <div style={{ color: colors.accent.warning }}>
                      <span style={{ color: colors.text.muted }}>Delay:</span> +{milestone.delay} months
                    </div>
                  )}
                  
                  {milestone.governance_status && (
                    <div style={{ color: colors.text.secondary }}>
                      <span style={{ color: colors.text.muted }}>Governance:</span> {milestone.governance_status}
                    </div>
                  )}
                </div>

                {milestone.pending_action && (
                  <div style={{ 
                    marginTop: spacing.sm, 
                    padding: `${spacing.xs} ${spacing.sm}`,
                    backgroundColor: `${colors.accent.warning}10`,
                    borderRadius: borderRadius.sm,
                    fontSize: typography.fontSize.sm,
                    color: colors.text.secondary,
                    role: 'alert',
                    'aria-live': 'polite'
                  }}>
                    ⚠️ {milestone.pending_action}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

export default memo(ProjectTimeline);
