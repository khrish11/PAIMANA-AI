import { Card, Button } from '../common';
import { colors, spacing, typography } from '../../tokens';
import { useNavigate } from 'react-router-dom';

export default function NodeDetails({ node, onClose }) {
  const navigate = useNavigate();

  if (!node) {
    return (
      <Card padding="lg">
        <div style={{ color: colors.text.muted, textAlign: 'center' }}>
          Select a node to view details
        </div>
      </Card>
    );
  }

  const handleViewProject = () => {
    if (node.node_type === 'PROJECT') {
      navigate(`/projects/${node.id}`);
    }
  };

  const handleViewIntelligence = () => {
    if (node.node_type === 'PROJECT') {
      navigate(`/projects/${node.id}/intelligence`);
    }
  };

  const handleDecisionCockpit = () => {
    if (node.node_type === 'PROJECT') {
      navigate(`/projects/${node.id}/decision-cockpit`);
    }
  };

  return (
    <Card padding="lg">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: spacing.lg }}>
        <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
          Node Details
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
          Type
        </div>
        <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
          {node.node_type}
        </div>
      </div>

      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
          Label
        </div>
        <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
          {node.label}
        </div>
      </div>

      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
          ID
        </div>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, wordBreak: 'break-all' }}>
          {node.id}
        </div>
      </div>

      {node.node_type === 'PROJECT' && (
        <>
          {node.risk_category && (
            <div style={{ marginBottom: spacing.lg }}>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                Risk Category
              </div>
              <div style={{ 
                fontSize: typography.fontSize.base, 
                fontWeight: 600,
                color: node.risk_category === 'CRITICAL' || node.risk_category === 'VERY_HIGH' 
                  ? colors.accent.danger 
                  : node.risk_category === 'HIGH' 
                    ? colors.accent.warning 
                    : colors.accent.success
              }}>
                {node.risk_category}
              </div>
            </div>
          )}

          {node.value !== undefined && (
            <div style={{ marginBottom: spacing.lg }}>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                Risk Score
              </div>
              <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
                {node.value.toFixed(1)}
              </div>
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
            <Button onClick={handleViewProject}>
              View Project
            </Button>
            <Button variant="secondary" onClick={handleViewIntelligence}>
              View Intelligence
            </Button>
            <Button variant="secondary" onClick={handleDecisionCockpit}>
              Open Decision Cockpit
            </Button>
          </div>
        </>
      )}

      {node.node_type !== 'PROJECT' && (
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
          Additional details for {node.node_type} nodes will be available when backend provides more metadata.
        </div>
      )}
    </Card>
  );
}
