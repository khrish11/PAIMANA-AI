import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function DecisionReadiness({ intelligence }) {
  const { data, availability } = intelligence;

  const risk = data.risk;
  const dcs = risk?.dcs;

  // Determine readiness dimensions
  const dimensions = [
    {
      name: 'RISK DATA',
      status: availability.risk === 'available' ? 'AVAILABLE' : 'UNAVAILABLE',
      available: availability.risk === 'available'
    },
    {
      name: 'FORECAST',
      status: availability.rcf === 'available' ? 'AVAILABLE' : 'UNAVAILABLE',
      available: availability.rcf === 'available'
    },
    {
      name: 'PEER BENCHMARK',
      status: availability.pbe === 'available' ? 'AVAILABLE' : 'UNAVAILABLE',
      available: availability.pbe === 'available'
    },
    {
      name: 'NARRATIVE',
      status: availability.nid === 'available' ? 'AVAILABLE' : 'UNAVAILABLE',
      available: availability.nid === 'available'
    },
    {
      name: 'DATA QUALITY',
      status: dcs && dcs.dcs_score >= 60 ? 'GOOD' : (dcs ? 'WARNING' : 'UNAVAILABLE'),
      available: availability.risk === 'available',
      warning: dcs && dcs.dcs_score < 60
    },
    {
      name: 'SIMULATION',
      status: 'AVAILABLE',
      available: true
    }
  ];

  // Count available and warning dimensions
  const availableCount = dimensions.filter(d => d.available).length;
  const warningCount = dimensions.filter(d => d.warning).length;
  const totalCount = dimensions.length;

  // Determine overall readiness
  let readiness = 'LIMITED';
  if (availableCount >= totalCount - 1 && warningCount === 0) {
    readiness = 'READY';
  } else if (availableCount >= totalCount / 2) {
    readiness = 'PARTIALLY READY';
  }

  const getReadinessColor = (status) => {
    switch (status) {
      case 'READY': return colors.accent.success;
      case 'PARTIALLY READY': return colors.accent.warning;
      case 'LIMITED': return colors.accent.danger;
      default: return colors.text.muted;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'AVAILABLE':
      case 'GOOD':
        return colors.accent.success;
      case 'WARNING':
        return colors.accent.warning;
      case 'UNAVAILABLE':
        return colors.text.muted;
      default:
        return colors.text.muted;
    }
  };

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          DECISION READINESS
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Capability and data quality summary for decision support.
        </p>
      </div>

      {/* Readiness Dimensions */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm, marginBottom: spacing.lg }}>
        {dimensions.map((dimension, index) => (
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
              {dimension.name}
            </div>
            <div style={{ 
              fontSize: typography.fontSize.sm,
              fontWeight: 600,
              color: getStatusColor(dimension.status)
            }}>
              {dimension.status}
            </div>
          </div>
        ))}
      </div>

      {/* Overall Readiness */}
      <div style={{ 
        padding: spacing.lg,
        backgroundColor: `${getReadinessColor(readiness)}10`,
        borderRadius: '0.5rem',
        border: `2px solid ${getReadinessColor(readiness)}30`,
        textAlign: 'center'
      }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
          DECISION READINESS
        </div>
        <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: getReadinessColor(readiness) }}>
          {readiness}
        </div>
      </div>

      {/* Legend */}
      <div style={{ marginTop: spacing.lg, display: 'flex', gap: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: colors.accent.success, borderRadius: '2px' }}></div>
          <span>Available / Good</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: colors.accent.warning, borderRadius: '2px' }}></div>
          <span>Warning</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: colors.text.muted, borderRadius: '2px' }}></div>
          <span>Unavailable</span>
        </div>
      </div>

      <div style={{ marginTop: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>NOTE:</strong> This is a capability/status summary, not an AI score. Readiness is based on data availability and quality.
      </div>
    </Card>
  );
}
