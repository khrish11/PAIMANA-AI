import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function RiskClusters({ nodes }) {
  if (!nodes || nodes.length === 0) {
    return (
      <Card padding="lg">
        <div style={{ color: colors.text.muted, textAlign: 'center' }}>
          No nodes available for cluster analysis
        </div>
      </Card>
    );
  }

  // Group projects by risk category
  const projectNodes = nodes.filter(n => n.node_type === 'PROJECT');
  const byRisk = projectNodes.reduce((acc, node) => {
    const risk = node.risk_category || 'UNKNOWN';
    if (!acc[risk]) {
      acc[risk] = [];
    }
    acc[risk].push(node);
    return acc;
  }, {});

  // Group by node type
  const byType = nodes.reduce((acc, node) => {
    if (!acc[node.node_type]) {
      acc[node.node_type] = [];
    }
    acc[node.node_type].push(node);
  return acc;
  }, {});

  return (
    <Card padding="lg">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Network Clusters
      </h3>

      {/* Risk Clusters */}
      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
          Projects by Risk Category
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
          {Object.entries(byRisk).map(([risk, riskNodes]) => (
            <div key={risk} style={{ 
              padding: spacing.sm,
              backgroundColor: colors.background.tertiary,
              borderRadius: '0.375rem',
              border: `1px solid ${colors.border.light}`
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
                  {risk}
                </span>
                <span style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
                  {riskNodes.length} projects
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Type Clusters */}
      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
          Nodes by Type
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
          {Object.entries(byType).map(([type, typeNodes]) => (
            <div key={type} style={{ 
              padding: spacing.sm,
              backgroundColor: colors.background.tertiary,
              borderRadius: '0.375rem',
              border: `1px solid ${colors.border.light}`
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
                  {type}
                </span>
                <span style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
                  {typeNodes.length} nodes
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>Note:</strong> Clusters are based on graph structure (risk category, node type). Systemic risk calculations require backend methodology.
      </div>
    </Card>
  );
}
