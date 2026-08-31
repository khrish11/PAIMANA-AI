import { Card, Badge, Button } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function DecisionHeader({ project, baseline, simulationStatus, onReset, onRefresh }) {
  const getStatusVariant = (status) => {
    switch (status) {
      case 'SIMULATING': return 'info';
      case 'COMPLETE': return 'success';
      case 'FAILED': return 'danger';
      default: return 'info';
    }
  };

  const getRiskCategoryVariant = (category) => {
    switch (category) {
      case 'CRITICAL': return 'critical';
      case 'VERY_HIGH': return 'danger';
      case 'HIGH': return 'warning';
      case 'MODERATE': return 'info';
      case 'LOW': return 'success';
      default: return 'info';
    }
  };

  return (
    <Card padding="lg">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: spacing.lg }}>
        <div>
          <h1 style={{ 
            fontSize: typography.fontSize['3xl'], 
            fontWeight: 700, 
            color: colors.text.primary, 
            marginBottom: spacing.xs 
          }}>
            DECISION COCKPIT
          </h1>
          <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
            Explore interventions, compare projected outcomes, and support evidence-based decisions.
          </p>
        </div>
        <div style={{ display: 'flex', gap: spacing.sm }}>
          <Button variant="ghost" onClick={onReset} disabled={simulationStatus === 'SIMULATING'}>
            Reset
          </Button>
          <Button variant="secondary" onClick={onRefresh} disabled={simulationStatus === 'SIMULATING'}>
            Refresh
          </Button>
        </div>
      </div>

      {project && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: spacing.md,
          padding: spacing.lg,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          marginBottom: spacing.lg
        }}>
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Project
            </div>
            <div style={{ fontWeight: 600, color: colors.text.primary }}>
              {project.project_name || 'N/A'}
            </div>
          </div>
          
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Project ID
            </div>
            <div style={{ fontWeight: 600, color: colors.text.primary, fontFamily: typography.fontFamily.mono }}>
              {project.project_id?.slice(0, 8)}...
            </div>
          </div>

          {baseline && (
            <>
              <div>
                <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                  Current Risk
                </div>
                <div style={{ fontWeight: 600, color: colors.text.primary }}>
                  {baseline.risk_score?.toFixed(1) || 'N/A'}
                </div>
              </div>

              <div>
                <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                  Risk Category
                </div>
                <Badge variant={getRiskCategoryVariant(baseline.risk_category)} size="md">
                  {baseline.risk_category || 'N/A'}
                </Badge>
              </div>
            </>
          )}

          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Simulation Status
            </div>
            <Badge variant={getStatusVariant(simulationStatus)} size="md">
              {simulationStatus}
            </Badge>
          </div>
        </div>
      )}

      <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        Last Updated: {new Date().toLocaleString()}
      </div>
    </Card>
  );
}
