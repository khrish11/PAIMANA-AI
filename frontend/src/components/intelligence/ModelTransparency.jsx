import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function ModelTransparency({ intelligence }) {
  const { data, availability } = intelligence;

  const risk = data.risk;
  const nid = data.nid;

  const models = [
    {
      name: 'Risk Model',
      version: risk?.ml_model_version || 'NOT AVAILABLE',
      status: risk?.ml_model_status || 'NOT AVAILABLE',
      available: availability.risk === 'available'
    },
    {
      name: 'Forecast Model (RCF)',
      version: 'rcf-engine-v1',
      status: 'AVAILABLE',
      available: availability.rcf === 'available'
    },
    {
      name: 'Peer Benchmark Model (PBE)',
      version: 'pbe-engine-v1',
      status: 'AVAILABLE',
      available: availability.pbe === 'available'
    },
    {
      name: 'Narrative Intelligence Model (NID)',
      version: nid?.model_version || 'NOT AVAILABLE',
      status: nid?.status || 'NOT AVAILABLE',
      available: availability.nid === 'available'
    }
  ];

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          MODEL TRANSPARENCY
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Model versions and data sources used for intelligence generation.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        {models.map((model, index) => (
          <div key={index} style={{ 
            padding: spacing.lg,
            backgroundColor: colors.background.tertiary,
            borderRadius: '0.5rem',
            border: `1px solid ${colors.border.light}`
          }}>
            <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
              {model.name}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: spacing.sm, fontSize: typography.fontSize.base, color: colors.text.secondary }}>
              <div>
                <span style={{ color: colors.text.muted }}>Version: </span>
                <span style={{ fontWeight: 600, color: colors.text.primary }}>{model.version}</span>
              </div>
              <div>
                <span style={{ color: colors.text.muted }}>Status: </span>
                <span style={{ fontWeight: 600, color: model.available ? colors.accent.success : colors.text.muted }}>
                  {model.available ? model.status : 'UNAVAILABLE'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Data Sources */}
      <div style={{ marginTop: spacing.lg, padding: spacing.lg, backgroundColor: colors.background.secondary, borderRadius: '0.5rem', border: `1px solid ${colors.border.light}` }}>
        <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.md }}>
          DATA SOURCES
        </div>
        <div style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          <div style={{ marginBottom: spacing.sm }}>
            <strong>Project Data:</strong> Financial records, progress reports, schedule data
          </div>
          <div style={{ marginBottom: spacing.sm }}>
            <strong>Reference Class:</strong> Historical project completion data
          </div>
          <div style={{ marginBottom: spacing.sm }}>
            <strong>Narrative:</strong> Project narrative text (if available)
          </div>
          <div>
            <strong>Last Updated:</strong> {risk?.reporting_month || 'N/A'}
          </div>
        </div>
      </div>

      <div style={{ marginTop: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>NOTE:</strong> Model versions are displayed when available from backend. Fabricated versions are not shown.
      </div>
    </Card>
  );
}
