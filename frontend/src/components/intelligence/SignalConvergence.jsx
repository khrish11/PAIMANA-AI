import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function SignalConvergence({ intelligence }) {
  const { data, availability } = intelligence;

  const getDirection = (value, threshold, inverse = false) => {
    if (value === null || value === undefined) return 'neutral';
    if (inverse) {
      if (value < threshold) return 'elevated';
      if (value > threshold) return 'reduced';
    } else {
      if (value > threshold) return 'elevated';
      if (value < threshold) return 'reduced';
    }
    return 'neutral';
  };

  const getStatusIcon = (direction) => {
    switch (direction) {
      case 'elevated': return '✓';
      case 'reduced': return '○';
      case 'neutral': return '○';
      default: return '—';
    }
  };

  const getStatusColor = (direction) => {
    switch (direction) {
      case 'elevated': return colors.accent.danger;
      case 'reduced': return colors.accent.success;
      case 'neutral': return colors.text.muted;
      default: return colors.text.muted;
    }
  };

  const risk = data.risk;
  const pbe = data.pbe;
  const rcf = data.rcf;
  const dcs = risk?.dcs;
  const nid = data.nid;
  const network = data.network;

  // Determine signal directions (elevated = concern, reduced = positive)
  const layers = [
    {
      name: 'RISK',
      direction: risk ? getDirection(risk.composite_score, 45) : 'unavailable',
      available: availability.risk === 'available'
    },
    {
      name: 'FORECAST',
      direction: rcf ? getDirection(rcf.p80_completion_months, 36) : 'unavailable',
      available: availability.rcf === 'available'
    },
    {
      name: 'PBE',
      direction: pbe ? getDirection(pbe.percentile, 50) : 'unavailable',
      available: availability.pbe === 'available'
    },
    {
      name: 'NID',
      direction: nid && nid.status === 'INCONSISTENT' ? 'elevated' : (nid ? 'neutral' : 'unavailable'),
      available: availability.nid === 'available'
    },
    {
      name: 'DCS',
      direction: dcs ? getDirection(dcs.dcs_score, 60, true) : 'unavailable',
      available: availability.risk === 'available' // DCS comes with risk
    },
    {
      name: 'NETWORK',
      direction: network && network.available ? (network.metadata?.high_risk_projects > 0 ? 'elevated' : 'neutral') : 'unavailable',
      available: availability.network === 'available'
    }
  ];

  // Count elevated signals
  const elevatedCount = layers.filter(l => l.direction === 'elevated').length;
  const availableCount = layers.filter(l => l.available).length;

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          SIGNAL CONVERGENCE
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          How many independent intelligence layers are pointing in the same direction?
        </p>
      </div>

      {/* Intelligence Layers */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm, marginBottom: spacing.lg }}>
        {layers.map((layer, index) => (
          <div key={index} style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            padding: spacing.md,
            backgroundColor: colors.background.tertiary,
            borderRadius: '0.375rem',
            border: `1px solid ${colors.border.light}`
          }}>
            <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
              {layer.name}
            </div>
            <div style={{ 
              fontSize: typography.fontSize['2xl'],
              fontWeight: 700,
              color: layer.available ? getStatusColor(layer.direction) : colors.text.muted
            }}>
              {layer.available ? getStatusIcon(layer.direction) : '—'}
            </div>
          </div>
        ))}
      </div>

      {/* Convergence Summary */}
      <div style={{ 
        padding: spacing.lg,
        backgroundColor: `${colors.accent.info}10`,
        borderRadius: '0.5rem',
        border: `1px solid ${colors.accent.info}30`,
        textAlign: 'center'
      }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
          SIGNAL CONVERGENCE
        </div>
        <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
          {elevatedCount} of {availableCount} intelligence layers indicate elevated concern
        </div>
      </div>

      {/* Legend */}
      <div style={{ marginTop: spacing.lg, display: 'flex', gap: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <span style={{ fontSize: typography.fontSize['2xl'], color: colors.accent.danger }}>✓</span>
          <span>Elevated concern</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <span style={{ fontSize: typography.fontSize['2xl'], color: colors.accent.success }}>○</span>
          <span>Reduced concern</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <span style={{ fontSize: typography.fontSize['2xl'], color: colors.text.muted }}>—</span>
          <span>Unavailable</span>
        </div>
      </div>

      <div style={{ marginTop: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>SOURCE:</strong> Risk Model, Reference Class Forecast, Peer Benchmark Engine, Narrative Intelligence Detection, Data Confidence Score, Network Intelligence
      </div>
    </Card>
  );
}
