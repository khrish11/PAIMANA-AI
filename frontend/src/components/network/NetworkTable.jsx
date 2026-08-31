import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function NetworkTable({ nodes, edges, onNodeClick }) {
  if (!nodes || nodes.length === 0) {
    return (
      <Card padding="lg">
        <div style={{ color: colors.text.muted, textAlign: 'center' }}>
          No nodes available
        </div>
      </Card>
    );
  }

  // Calculate connections per node
  const nodeConnections = {};
  edges.forEach(edge => {
    nodeConnections[edge.source] = (nodeConnections[edge.source] || 0) + 1;
    nodeConnections[edge.target] = (nodeConnections[edge.target] || 0) + 1;
  });

  const getRiskColor = (risk) => {
    if (risk === 'CRITICAL' || risk === 'VERY_HIGH') return colors.accent.danger;
    if (risk === 'HIGH') return colors.accent.warning;
    if (risk === 'MODERATE') return colors.accent.info;
    return colors.accent.success;
  };

  return (
    <Card padding="lg">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Network Nodes (Table View)
      </h3>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: typography.fontSize.sm }}>
          <thead>
            <tr style={{ borderBottom: `2px solid ${colors.border.light}`, textAlign: 'left' }}>
              <th style={{ padding: spacing.sm, color: colors.text.muted, fontWeight: 600 }}>Label</th>
              <th style={{ padding: spacing.sm, color: colors.text.muted, fontWeight: 600 }}>Type</th>
              <th style={{ padding: spacing.sm, color: colors.text.muted, fontWeight: 600 }}>Risk</th>
              <th style={{ padding: spacing.sm, color: colors.text.muted, fontWeight: 600 }}>Connections</th>
              <th style={{ padding: spacing.sm, color: colors.text.muted, fontWeight: 600 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {nodes.map((node, index) => (
              <tr 
                key={index}
                style={{ borderBottom: `1px solid ${colors.border.light}`, cursor: 'pointer' }}
                onClick={() => onNodeClick && onNodeClick(node)}
              >
                <td style={{ padding: spacing.sm, color: colors.text.primary }}>
                  {node.label}
                </td>
                <td style={{ padding: spacing.sm, color: colors.text.secondary }}>
                  {node.node_type}
                </td>
                <td style={{ padding: spacing.sm }}>
                  {node.risk_category ? (
                    <span style={{ 
                      padding: `${spacing.xs} ${spacing.sm}`,
                      backgroundColor: `${getRiskColor(node.risk_category)}20`,
                      borderRadius: '0.25rem',
                      fontSize: typography.fontSize.xs,
                      fontWeight: 600,
                      color: getRiskColor(node.risk_category)
                    }}>
                      {node.risk_category}
                    </span>
                  ) : (
                    <span style={{ color: colors.text.muted }}>—</span>
                  )}
                </td>
                <td style={{ padding: spacing.sm, color: colors.text.primary }}>
                  {nodeConnections[node.id] || 0}
                </td>
                <td style={{ padding: spacing.sm }}>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onNodeClick && onNodeClick(node);
                    }}
                    style={{
                      padding: `${spacing.xs} ${spacing.sm}`,
                      fontSize: typography.fontSize.xs,
                      backgroundColor: colors.background.secondary,
                      border: `1px solid ${colors.border.light}`,
                      borderRadius: '0.25rem',
                      cursor: 'pointer'
                    }}
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        Showing {nodes.length} nodes
      </div>
    </Card>
  );
}
