import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function ProvenancePanel({ intelligence }) {
  const { data } = intelligence;

  const risk = data.risk;
  const pbe = data.pbe;
  const rcf = data.rcf;
  const dcs = risk?.dcs;
  const nid = data.nid;

  const provenanceItems = [];

  // Risk provenance
  if (risk) {
    provenanceItems.push({
      signal: 'Risk Score',
      source: 'Project Financial Data',
      model: 'Risk Model',
      timestamp: risk.reporting_month || 'N/A',
      dataStatus: 'AVAILABLE',
      confidence: dcs?.dcs_score ? `${dcs.dcs_score.toFixed(0)}%` : 'UNAVAILABLE'
    });
  }

  // PBE provenance
  if (pbe) {
    provenanceItems.push({
      signal: 'Peer Percentile',
      source: 'Peer Project Database',
      model: 'Peer Benchmark Engine',
      timestamp: 'N/A',
      dataStatus: 'AVAILABLE',
      confidence: 'NOT PROVIDED'
    });
  }

  // RCF provenance
  if (rcf) {
    provenanceItems.push({
      signal: 'Forecast Quantiles',
      source: 'Reference Class Database',
      model: 'Reference Class Forecast',
      timestamp: 'N/A',
      dataStatus: rcf.used_fallback ? 'FALLBACK' : 'AVAILABLE',
      confidence: 'NOT PROVIDED'
    });
  }

  // NID provenance
  if (nid) {
    provenanceItems.push({
      signal: 'Narrative Consistency',
      source: 'Project Narrative Text',
      model: 'Narrative Intelligence Detection',
      timestamp: 'N/A',
      dataStatus: nid.status === 'INCONSISTENT' ? 'INCONSISTENT' : 'AVAILABLE',
      confidence: nid.confidence || 'NOT PROVIDED'
    });
  }

  // DCS provenance
  if (dcs) {
    provenanceItems.push({
      signal: 'Data Confidence',
      source: 'Project Data Records',
      model: 'Data Confidence Score',
      timestamp: 'N/A',
      dataStatus: 'AVAILABLE',
      confidence: `${dcs.dcs_score.toFixed(0)}%`
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
          EVIDENCE PROVENANCE
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Source, model, timestamp, and confidence for major signals.
        </p>
      </div>

      {provenanceItems.length === 0 ? (
        <div style={{ 
          padding: spacing.xl,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          textAlign: 'center',
          color: colors.text.muted
        }}>
          No provenance data available.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
          {provenanceItems.map((item, index) => (
            <div key={index} style={{ 
              padding: spacing.lg,
              backgroundColor: colors.background.tertiary,
              borderRadius: '0.5rem',
              border: `1px solid ${colors.border.light}`
            }}>
              <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
                {item.signal}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: spacing.sm, fontSize: typography.fontSize.base, color: colors.text.secondary }}>
                <div>
                  <span style={{ color: colors.text.muted }}>Source: </span>
                  <span style={{ fontWeight: 600, color: colors.text.primary }}>{item.source}</span>
                </div>
                <div>
                  <span style={{ color: colors.text.muted }}>Model: </span>
                  <span style={{ fontWeight: 600, color: colors.text.primary }}>{item.model}</span>
                </div>
                <div>
                  <span style={{ color: colors.text.muted }}>Updated: </span>
                  <span style={{ fontWeight: 600, color: colors.text.primary }}>{item.timestamp}</span>
                </div>
                <div>
                  <span style={{ color: colors.text.muted }}>Data Status: </span>
                  <span style={{ fontWeight: 600, color: colors.text.primary }}>{item.dataStatus}</span>
                </div>
                <div>
                  <span style={{ color: colors.text.muted }}>Confidence: </span>
                  <span style={{ fontWeight: 600, color: colors.text.primary }}>{item.confidence}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>NOTE:</strong> Provenance information is displayed when available from backend. Fabricated provenance is not shown.
      </div>
    </Card>
  );
}
