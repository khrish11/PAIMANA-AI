import { Card, Button } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function AttentionQueue({ intelligence }) {
  const { data } = intelligence;

  const risk = data.risk;
  const pbe = data.pbe;
  const rcf = data.rcf;
  const dcs = risk?.dcs;
  const nid = data.nid;

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return colors.accent.danger;
      case 'HIGH': return colors.accent.warning;
      case 'MODERATE': return colors.accent.info;
      case 'LOW': return colors.accent.success;
      default: return colors.text.muted;
    }
  };

  // Generate attention items from available signals
  const attentionItems = [];

  // Critical Risk
  if (risk && risk.composite_score >= 75) {
    attentionItems.push({
      project: risk.project_name || 'Current Project',
      signal: 'CRITICAL RISK',
      severity: 'CRITICAL',
      evidence: `Risk score: ${risk.composite_score.toFixed(1)}`,
      lastUpdated: risk.reporting_month || 'N/A',
      action: 'VIEW PROJECT'
    });
  }

  // Risk Movement (if trend shows deterioration)
  if (data.trend && data.trend.trend && data.trend.trend.length > 1) {
    const trend = data.trend.trend;
    const latest = trend[trend.length - 1];
    const previous = trend[trend.length - 2];
    if (latest.composite_score > previous.composite_score + 10) {
      attentionItems.push({
        project: risk.project_name || 'Current Project',
        signal: 'RISK MOVEMENT',
        severity: latest.composite_score > 60 ? 'HIGH' : 'MODERATE',
        evidence: `Risk increased from ${previous.composite_score.toFixed(1)} to ${latest.composite_score.toFixed(1)}`,
        lastUpdated: latest.reporting_month,
        action: 'VIEW EVIDENCE'
      });
    }
  }

  // Forecast Pressure
  if (rcf && rcf.p80_completion_months > 48) {
    attentionItems.push({
      project: risk.project_name || 'Current Project',
      signal: 'FORECAST PRESSURE',
      severity: rcf.p80_completion_months > 60 ? 'HIGH' : 'MODERATE',
      evidence: `P80 completion: ${rcf.p80_completion_months.toFixed(0)} months`,
      lastUpdated: 'N/A',
      action: 'VIEW FORECAST'
    });
  }

  // Peer Underperformance
  if (pbe && pbe.percentile > 70) {
    attentionItems.push({
      project: risk.project_name || 'Current Project',
      signal: 'PEER UNDERPERFORMANCE',
      severity: pbe.percentile > 85 ? 'HIGH' : 'MODERATE',
      evidence: `${pbe.percentile.toFixed(0)}th percentile (worse than peers)`,
      lastUpdated: 'N/A',
      action: 'VIEW PEER INTELLIGENCE'
    });
  }

  // Narrative Inconsistency
  if (nid && nid.status === 'INCONSISTENT' && nid.contradictions && nid.contradictions.length > 0) {
    attentionItems.push({
      project: risk.project_name || 'Current Project',
      signal: 'NARRATIVE INCONSISTENCY',
      severity: 'MODERATE',
      evidence: `${nid.contradictions.length} contradictions detected`,
      lastUpdated: 'N/A',
      action: 'VIEW NARRATIVE'
    });
  }

  // Data Quality
  if (dcs && dcs.dcs_score < 50) {
    attentionItems.push({
      project: risk.project_name || 'Current Project',
      signal: 'DATA QUALITY',
      severity: dcs.dcs_score < 30 ? 'HIGH' : 'MODERATE',
      evidence: `DCS score: ${dcs.dcs_score.toFixed(0)}%`,
      lastUpdated: 'N/A',
      action: 'VIEW DATA HEALTH'
    });
  }

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          ATTENTION QUEUE
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Projects and signals that deserve human attention.
        </p>
      </div>

      {attentionItems.length === 0 ? (
        <div style={{ 
          padding: spacing.xl,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          textAlign: 'center',
          color: colors.text.muted
        }}>
          No attention items based on current intelligence data.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
          {attentionItems.map((item, index) => (
            <div key={index} style={{ 
              padding: spacing.lg,
              backgroundColor: colors.background.tertiary,
              borderRadius: '0.5rem',
              border: `1px solid ${colors.border.light}`,
              borderLeft: `4px solid ${getSeverityColor(item.severity)}`
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: spacing.sm }}>
                <div>
                  <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
                    {item.project}
                  </div>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginTop: spacing.xs }}>
                    {item.signal}
                  </div>
                </div>
                <div style={{ 
                  padding: `${spacing.xs} ${spacing.sm}`,
                  backgroundColor: `${getSeverityColor(item.severity)}20`,
                  borderRadius: '0.25rem',
                  fontSize: typography.fontSize.sm,
                  fontWeight: 600,
                  color: getSeverityColor(item.severity)
                }}>
                  {item.severity}
                </div>
              </div>
              <div style={{ fontSize: typography.fontSize.base, color: colors.text.secondary, marginBottom: spacing.sm }}>
                {item.evidence}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: typography.fontSize.sm }}>
                <span style={{ color: colors.text.muted }}>Updated: {item.lastUpdated}</span>
                <Button variant="secondary" size="sm">
                  {item.action}
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>NOTE:</strong> This queue is for attention identification. No automated decision execution is performed.
      </div>
    </Card>
  );
}
