import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function DependencyPath({ paths }) {
  if (!paths || paths.length === 0) {
    return (
      <Card padding="lg">
        <div style={{ color: colors.text.muted, textAlign: 'center' }}>
          No dependency paths available
        </div>
      </Card>
    );
  }

  return (
    <Card padding="lg">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Dependency Paths
      </h3>

      <div style={{ maxHeight: '400px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
        {paths.slice(0, 50).map((path, index) => (
          <div 
            key={index}
            style={{ 
              padding: spacing.md,
              backgroundColor: colors.background.tertiary,
              borderRadius: '0.375rem',
              border: `1px solid ${colors.border.light}`
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.xs }}>
              <span style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
                {path.depth} hop{path.depth > 1 ? 's' : ''}:
              </span>
              <span style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
                {path.from}
              </span>
              <span style={{ fontSize: typography.fontSize['2xl'], color: colors.accent.primary }}>
                →
              </span>
              <span style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
                {path.to}
              </span>
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              Relationship: {path.relationship}
            </div>
          </div>
        ))}
        {paths.length > 50 && (
          <div style={{ textAlign: 'center', fontSize: typography.fontSize.sm, color: colors.text.muted }}>
            ... and {paths.length - 50} more paths
          </div>
        )}
      </div>

      <div style={{ marginTop: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        Showing {Math.min(paths.length, 50)} of {paths.length} paths
      </div>
    </Card>
  );
}
