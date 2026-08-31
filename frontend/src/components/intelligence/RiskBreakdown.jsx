import { Card, Button } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';

function RiskBreakdown({ riskData, onWhyClick }) {
  if (!riskData) {
    return (
      <Card padding="lg">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          Risk breakdown unavailable
        </div>
      </Card>
    );
  }

  const components = riskData.component_scores || {};

  const maxScore = Math.max(
    components.cost_risk || 0,
    components.schedule_risk || 0,
    components.progress_risk || 0,
    components.governance_risk || 0,
    1
  );

  const renderBar = (label, value, color) => {
    const percentage = (value / maxScore) * 100;
    return (
      <div style={{ marginBottom: spacing.md }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: spacing.xs }}>
          <span style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
            {label}
          </span>
          <span style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.primary }}>
            {value?.toFixed(1) || 'N/A'}
          </span>
        </div>
        <div
          style={{
            height: '8px',
            backgroundColor: colors.background.tertiary,
            borderRadius: borderRadius.full,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              height: '100%',
              width: `${percentage}%`,
              backgroundColor: color,
              transition: 'width 300ms ease-in-out',
            }}
          />
        </div>
      </div>
    );
  };

  return (
    <Card padding="lg">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.lg }}>
        <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
          Risk Decomposition
        </h3>
        <Button variant="ghost" size="sm" onClick={onWhyClick}>
          Why?
        </Button>
      </div>

      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
          Composite Risk
        </div>
        <div style={{ fontSize: typography.fontSize['4xl'], fontWeight: 700, color: colors.text.primary }}>
          {riskData.composite_score?.toFixed(1) || 'N/A'}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
        {renderBar('Cost Risk', components.cost_risk, colors.accent.danger)}
        {renderBar('Schedule Risk', components.schedule_risk, colors.accent.warning)}
        {renderBar('Progress Risk', components.progress_risk, colors.accent.primary)}
        {renderBar('Governance Risk', components.governance_risk, colors.accent.secondary)}
      </div>
    </Card>
  );
}

export default RiskBreakdown;
