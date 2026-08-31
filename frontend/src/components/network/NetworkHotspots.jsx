import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function NetworkHotspots({ nodes, edges }) {
  if (!nodes || !edges) {
    return (
      <Card padding="lg">
        <div style={{ color: colors.text.muted, textAlign: 'center' }}>
          No network data available for hotspot analysis
        </div>
      </Card>
    );
  }

  // Calculate node degrees (number of connections)
  const nodeDegrees = {};
  edges.forEach(edge => {
    nodeDegrees[edge.source] = (nodeDegrees[edge.source] || 0) + 1;
    nodeDegrees[edge.target] = (nodeDegrees[edge.target] || 0) + 1;
  });

  // Find top connected nodes
  const sortedNodes = Object.entries(nodeDegrees)
    .map(([nodeId, degree]) => ({
      node: nodes.find(n => n.id === nodeId),
      degree
    }))
    .filter(item => item.node)
    .sort((a, b) => b.degree - a.degree)
    .slice(0, 10);

  // Group by type
  const byType = sortedNodes.reduce((acc, item) => {
    const type = item.node.node_type;
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(item);
    return acc;
  }, {});

  return (
    <Card padding="lg">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Network Hotspots
      </h3>

      <div style={{ marginBottom: spacing.md }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
          <strong>Methodology:</strong> High connectivity based on number of linked nodes in the network graph.
        </div>
      </div>

      {sortedNodes.length === 0 ? (
        <div style={{ padding: spacing.md, backgroundColor: colors.background.tertiary, borderRadius: '0.375rem', textAlign: 'center', color: colors.text.muted }}>
          No highly connected nodes found
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
          {Object.entries(byType).map(([type, items]) => (
            <div key={type}>
              <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
                {type} Hotspots
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
                {items.map((item, index) => (
                  <div key={index} style={{ 
                    padding: spacing.sm,
                    backgroundColor: colors.background.tertiary,
                    borderRadius: '0.375rem',
                    border: `1px solid ${colors.border.light}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div>
                      <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
                        {item.node.label}
                      </div>
                      <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
                        {item.node.id}
                      </div>
                    </div>
                    <div style={{ fontSize: typography.fontSize.lg, fontWeight: 700, color: colors.accent.primary }}>
                      {item.degree}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>Note:</strong> This identifies nodes with high graph connectivity. It does not represent systemic risk unless backend establishes that relationship.
      </div>
    </Card>
  );
}
