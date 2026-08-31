import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function EdgeDetails({ edge, onClose }) {
  if (!edge) {
    return (
      <Card padding="lg">
        <div style={{ color: colors.text.muted, textAlign: 'center' }}>
          Select an edge to view details
        </div>
      </Card>
    );
  }

  return (
    <Card padding="lg">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: spacing.lg }}>
        <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
          Edge Details
        </h3>
        <button 
          onClick={onClose}
          style={{ 
            background: 'none', 
            border: 'none', 
            fontSize: typography.fontSize['2xl'], 
            cursor: 'pointer',
            color: colors.text.muted
          }}
        >
          ×
        </button>
      </div>

      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
          Source
        </div>
        <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary, wordBreak: 'break-all' }}>
          {edge.source}
        </div>
      </div>

      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
          Target
        </div>
        <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary, wordBreak: 'break-all' }}>
          {edge.target}
        </div>
      </div>

      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
          Relationship Type
        </div>
        <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.accent.primary }}>
          {edge.relationship_type}
        </div>
      </div>

      {edge.weight !== undefined && (
        <div style={{ marginBottom: spacing.lg }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            Weight
          </div>
          <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
            {edge.weight}
          </div>
        </div>
      )}

      <div style={{ marginTop: spacing.lg, padding: spacing.md, backgroundColor: `${colors.accent.warning}10`, borderRadius: '0.375rem', border: `1px solid ${colors.accent.warning}30` }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
          <strong>Note:</strong> This represents a relationship in the network graph. It does not imply causality or operational impact unless explicitly supported by backend analysis.
        </div>
      </div>
    </Card>
  );
}
