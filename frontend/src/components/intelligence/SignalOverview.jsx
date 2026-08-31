import { Card, Badge } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function SignalOverview({ intelligence }) {
  const { data } = intelligence;

  const getRiskCategory = (score) => {
    if (score === null || score === undefined) return 'N/A';
    if (score >= 75) return 'CRITICAL';
    if (score >= 60) return 'VERY_HIGH';
    if (score >= 45) return 'HIGH';
    if (score >= 30) return 'MODERATE';
    return 'LOW';
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return colors.accent.danger;
      case 'HIGH': return colors.accent.warning;
      case 'MODERATE': return colors.accent.info;
      case 'LOW': return colors.accent.success;
      default: return colors.text.muted;
    }
  };

  const getSeverityBadgeVariant = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'critical';
      case 'HIGH': return 'danger';
      case 'MODERATE': return 'warning';
      case 'LOW': return 'success';
      default: return 'info';
    }
  };

  const risk = data.risk;
  const pbe = data.pbe;
  const dcs = risk?.dcs;
  const nid = data.nid;

  // Generate signals from available data
  const signals = [];

  // Risk signal
  if (risk && risk.composite_score !== null) {
    const category = getRiskCategory(risk.composite_score);
    if (category === 'CRITICAL' || category === 'VERY_HIGH' || category === 'HIGH') {
      signals.push({
        name: 'Elevated Risk',
        severity: category,
        value: `${risk.composite_score.toFixed(1)}`,
        source: 'Risk Model',
        lastUpdated: risk.reporting_month || 'N/A'
      });
    }
  }

  // Risk deterioration signal (if trend available)
  if (data.trend && data.trend.trend && data.trend.trend.length > 1) {
    const trend = data.trend.trend;
    const latest = trend[trend.length - 1];
    const previous = trend[trend.length - 2];
    if (latest.composite_score > previous.composite_score + 5) {
      signals.push({
        name: 'Risk Deterioration',
        severity: latest.composite_score > 60 ? 'HIGH' : 'MODERATE',
        value: `${previous.composite_score.toFixed(1)} → ${latest.composite_score.toFixed(1)}`,
        source: 'Risk Trend',
        lastUpdated: latest.reporting_month
      });
    }
  }

  // Peer underperformance signal
  if (pbe && pbe.percentile !== null && pbe.percentile > 60) {
    signals.push({
      name: 'Peer Underperformance',
      severity: pbe.percentile > 80 ? 'HIGH' : 'MODERATE',
      value: `${pbe.percentile.toFixed(0)}th percentile`,
      source: 'Peer Benchmark Engine',
      lastUpdated: 'N/A'
    });
  }

  // Data quality signal
  if (dcs && dcs.dcs_score !== null && dcs.dcs_score < 60) {
    signals.push({
      name: 'Low Data Quality',
      severity: dcs.dcs_score < 40 ? 'HIGH' : 'MODERATE',
      value: `${dcs.dcs_score.toFixed(0)}%`,
      source: 'Data Confidence Score',
      lastUpdated: 'N/A'
    });
  }

  // Narrative inconsistency signal
  if (nid && nid.status === 'INCONSISTENT' && nid.contradictions && nid.contradictions.length > 0) {
    signals.push({
      name: 'Narrative Inconsistency',
      severity: 'MODERATE',
      value: `${nid.contradictions.length} contradictions`,
      source: 'Narrative Intelligence Detection',
      lastUpdated: 'N/A'
    });
  }

  // Schedule pressure signal (from RCF)
  if (data.rcf && data.rcf.p80_completion_months !== null && data.rcf.p80_completion_months > 48) {
    signals.push({
      name: 'Schedule Pressure',
      severity: data.rcf.p80_completion_months > 60 ? 'HIGH' : 'MODERATE',
      value: `${data.rcf.p80_completion_months.toFixed(0)} months`,
      source: 'Reference Class Forecast',
      lastUpdated: 'N/A'
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
          SIGNAL OVERVIEW
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Strongest currently available signals from intelligence layers.
        </p>
      </div>

      {signals.length === 0 ? (
        <div style={{ 
          padding: spacing.xl,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          textAlign: 'center',
          color: colors.text.muted
        }}>
          No elevated signals detected based on available intelligence data.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
          {signals.map((signal, index) => (
            <div key={index} style={{ 
              padding: spacing.lg,
              backgroundColor: colors.background.tertiary,
              borderRadius: '0.5rem',
              border: `1px solid ${colors.border.light}`,
              borderLeft: `4px solid ${getSeverityColor(signal.severity)}`
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: spacing.sm }}>
                <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
                  {signal.name}
                </div>
                <Badge variant={getSeverityBadgeVariant(signal.severity)} size="sm">
                  {signal.severity}
                </Badge>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: spacing.sm, fontSize: typography.fontSize.base, color: colors.text.secondary }}>
                <div>
                  <span style={{ color: colors.text.muted }}>Value: </span>
                  <span style={{ fontWeight: 600, color: colors.text.primary }}>{signal.value}</span>
                </div>
                <div>
                  <span style={{ color: colors.text.muted }}>Source: </span>
                  <span style={{ fontWeight: 600, color: colors.text.primary }}>{signal.source}</span>
                </div>
                <div>
                  <span style={{ color: colors.text.muted }}>Updated: </span>
                  <span style={{ fontWeight: 600, color: colors.text.primary }}>{signal.lastUpdated}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>SOURCE:</strong> Signals derived from Risk Model, Reference Class Forecast, Peer Benchmark Engine, Data Confidence Score, Narrative Intelligence Detection
      </div>
    </Card>
  );
}
