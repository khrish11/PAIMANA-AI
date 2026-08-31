import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function CriticalDependencies({ edges, nodes }) {
  if (!edges || edges.length === 0) {
    return (
      <Card padding="lg">
        <div style={{ color: colors.text.muted, textAlign: 'center' }}>
          No dependencies available
        </div>
      </Card>
    );
  }

  // Group edges by relationship type
  const byRelationship = edges.reduce((acc, edge) => {
    if (!acc[edge.relationship_type]) {
      acc[edge.relationship_type] = [];
    }
    acc[edge.relationship_type].push(edge);
    return acc;
  }, {});

  return (
    <Card padding="lg">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Key Dependencies
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        {Object.entries(byRelationship).map(([relationship, relEdges]) => (
          <div key={relationship}>
            <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
              {relationship} ({relEdges.length})
            </div>
            <div style={{ maxHeight: '150px', overflowY: 'auto', fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              {relEdges.slice(0, 10).map((edge, index) => {
                const sourceNode = nodes.find(n => n.id === edge.source);
                const targetNode = nodes.find(n => n.id === edge.target);
                return (
                  <div key={index} style={{ padding: spacing.xs, borderBottom: `1px solid ${colors.border.light}` }}>
                    {sourceNode?.label || edge.source} → {targetNode?.label || edge.target}
                  </div>
                );
              })}
              {relEdges.length > 10 && (
                <div style={{ padding: spacing.xs, color: colors.text.muted }}>
                  ... and {relEdges.length - 10} more
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: spacing.lg, padding: spacing.md, backgroundColor: `${colors.accent.warning}10`, borderRadius: '0.375rem', border: `1px solid ${colors.accent.warning}30` }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
          <strong>Note:</strong> These are key relationships in the network graph. Classification as &ldquo;critical&rdquo; requires backend criteria.
        </div>
      </div>
    </Card>
  );
}
