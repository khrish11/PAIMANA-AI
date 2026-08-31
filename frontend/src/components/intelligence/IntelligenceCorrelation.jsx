import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function IntelligenceCorrelation({ intelligence }) {
  const { data } = intelligence;

  const getRiskCategory = (score) => {
    if (score === null || score === undefined) return 'N/A';
    if (score >= 75) return 'CRITICAL';
    if (score >= 60) return 'VERY_HIGH';
    if (score >= 45) return 'HIGH';
    if (score >= 30) return 'MODERATE';
    return 'LOW';
  };

  const getDirection = (value, threshold) => {
    if (value === null || value === undefined) return 'neutral';
    if (value > threshold) return 'elevated';
    if (value < threshold) return 'reduced';
    return 'neutral';
  };

  const risk = data.risk;
  const pbe = data.pbe;
  const rcf = data.rcf;
  const dcs = risk?.dcs;
  const nid = data.nid;

  // Determine signal directions
  const riskDirection = risk ? getDirection(risk.composite_score, 45) : 'neutral';
  const peerDirection = pbe ? getDirection(pbe.percentile, 50) : 'neutral';
  const forecastDirection = rcf ? getDirection(rcf.p80_completion_months, 36) : 'neutral';
  const dataDirection = dcs ? getDirection(dcs.dcs_score, 60) : 'neutral';

  // Generate correlation observations (frontend correlation, not backend statistical)
  const correlations = [];

  // Risk ↔ Forecast correlation
  if (risk && rcf) {
    const riskElevated = riskDirection === 'elevated';
    const forecastElevated = forecastDirection === 'elevated';
    
    if (riskElevated && forecastElevated) {
      correlations.push({
        from: 'RISK',
        fromValue: `${risk.composite_score.toFixed(1)} (${getRiskCategory(risk.composite_score)})`,
        to: 'FORECAST',
        toValue: `${rcf.p80_completion_months?.toFixed(0) || 'N/A'} months`,
        relationship: 'Signals are aligned',
        source: 'Frontend correlation observation',
        backendSupported: false
      });
    }
  }

  // Risk ↔ Peer correlation
  if (risk && pbe) {
    const riskElevated = riskDirection === 'elevated';
    const peerElevated = peerDirection === 'elevated';
    
    if (riskElevated && peerElevated) {
      correlations.push({
        from: 'RISK',
        fromValue: `${risk.composite_score.toFixed(1)} (${getRiskCategory(risk.composite_score)})`,
        to: 'PBE',
        toValue: `${pbe.percentile?.toFixed(0) || 'N/A'}th percentile`,
        relationship: 'Signals are aligned',
        source: 'Frontend correlation observation',
        backendSupported: false
      });
    }
  }

  // Risk ↔ Data correlation
  if (risk && dcs) {
    const riskElevated = riskDirection === 'elevated';
    const dataReduced = dataDirection === 'reduced';
    
    if (riskElevated && dataReduced) {
      correlations.push({
        from: 'RISK',
        fromValue: `${risk.composite_score.toFixed(1)} (${getRiskCategory(risk.composite_score)})`,
        to: 'DCS',
        toValue: `${dcs.dcs_score?.toFixed(0) || 'N/A'}%`,
        relationship: 'Signals are aligned',
        source: 'Frontend correlation observation',
        backendSupported: false
      });
    }
  }

  // NID ↔ Quantitative correlation
  if (nid && risk) {
    if (nid.status === 'INCONSISTENT' && riskDirection === 'elevated') {
      correlations.push({
        from: 'NID',
        fromValue: 'INCONSISTENT',
        to: 'RISK',
        toValue: `${risk.composite_score.toFixed(1)} (${getRiskCategory(risk.composite_score)})`,
        relationship: 'Narrative/quantitative inconsistency observed',
        source: 'Frontend correlation observation',
        backendSupported: false
      });
    }
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
          INTELLIGENCE CORRELATION
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Observed relationships between intelligence systems.
        </p>
      </div>

      {correlations.length === 0 ? (
        <div style={{ 
          padding: spacing.xl,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          textAlign: 'center',
          color: colors.text.muted
        }}>
          No significant correlations observed based on available intelligence data.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
          {correlations.map((correlation, index) => (
            <div key={index} style={{ 
              padding: spacing.lg,
              backgroundColor: colors.background.tertiary,
              borderRadius: '0.5rem',
              border: `1px solid ${colors.border.light}`
            }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md, alignItems: 'center' }}>
                {/* From */}
                <div style={{ 
                  padding: spacing.md,
                  backgroundColor: colors.background.secondary,
                  borderRadius: '0.375rem',
                  textAlign: 'center',
                  minWidth: '200px'
                }}>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                    {correlation.from}
                  </div>
                  <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
                    {correlation.fromValue}
                  </div>
                </div>

                {/* Arrow */}
                <div style={{ 
                  fontSize: typography.fontSize['2xl'],
                  color: colors.accent.primary,
                  fontWeight: 700
                }}>
                  ↓
                </div>

                {/* To */}
                <div style={{ 
                  padding: spacing.md,
                  backgroundColor: colors.background.secondary,
                  borderRadius: '0.375rem',
                  textAlign: 'center',
                  minWidth: '200px'
                }}>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                    {correlation.to}
                  </div>
                  <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
                    {correlation.toValue}
                  </div>
                </div>

                {/* Relationship */}
                <div style={{ 
                  padding: spacing.md,
                  backgroundColor: `${colors.accent.info}10`,
                  borderRadius: '0.375rem',
                  border: `1px solid ${colors.accent.info}30`,
                  textAlign: 'center',
                  fontSize: typography.fontSize.base,
                  color: colors.text.secondary,
                  fontWeight: 500
                }}>
                  {correlation.relationship}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: spacing.lg, padding: spacing.md, backgroundColor: colors.background.secondary, borderRadius: '0.375rem', border: `1px solid ${colors.border.light}` }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
          <strong>IMPORTANT:</strong> Correlations shown are frontend observations of signal alignment. Statistical correlation requires backend calculation.
        </div>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
          <strong>SOURCE:</strong> Risk Model, Reference Class Forecast, Peer Benchmark Engine, Data Confidence Score, Narrative Intelligence Detection
        </div>
      </div>
    </Card>
  );
}
