import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';
import { memo } from 'react';

function NIDSummary({ nidData }) {
  if (!nidData) {
    return (
      <Card padding="lg" role="region" aria-label="NID Summary">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          NID analysis unavailable
        </div>
      </Card>
    );
  }

  const contradictions = nidData.contradictions || [];
  const highSeverity = contradictions.filter(c => c.severity === 'HIGH' || c.severity === 'CRITICAL').length;
  const mediumSeverity = contradictions.filter(c => c.severity === 'MODERATE').length;
  const lowSeverity = contradictions.filter(c => c.severity === 'LOW').length;

  return (
    <Card padding="lg" role="region" aria-label="NID Summary">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        NID Summary
      </h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: spacing.md }}>
        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            Claims Analyzed
          </div>
          <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
            {nidData.extracted_claims?.length || 0}
          </div>
        </div>

        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            Contradictions Detected
          </div>
          <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
            {contradictions.length}
          </div>
        </div>

        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            High Severity
          </div>
          <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.accent.danger }}>
            {highSeverity}
          </div>
        </div>

        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            Medium Severity
          </div>
          <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.accent.warning }}>
            {mediumSeverity}
          </div>
        </div>

        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            Low Severity
          </div>
          <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.accent.info }}>
            {lowSeverity}
          </div>
        </div>

        <div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            NQC Score
          </div>
          <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
            {nidData.nqc_score?.toFixed(0) || 'N/A'}
          </div>
        </div>
      </div>

      {nidData.model_version && (
        <div style={{ marginTop: spacing.lg, paddingTop: spacing.md, borderTop: `1px solid ${colors.border.default}` }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
            Model: {nidData.model_version} | Confidence: {nidData.confidence || 'N/A'}
          </div>
        </div>
      )}
    </Card>
  );
}

export default memo(NIDSummary);
