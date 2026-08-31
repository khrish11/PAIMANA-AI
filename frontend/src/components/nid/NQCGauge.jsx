import { Card, Badge } from '../common';
import { colors, spacing, typography } from '../../tokens';
import { memo } from 'react';

function NQCGauge({ nqcScore, confidence }) {
  if (nqcScore === null || nqcScore === undefined) {
    return (
      <Card padding="lg" role="region" aria-label="NQC Score">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          NQC UNAVAILABLE
        </div>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, marginTop: spacing.sm }}>
          Insufficient narrative or quantitative evidence.
        </div>
      </Card>
    );
  }

  const getNQCColor = (score) => {
    if (score >= 80) return colors.accent.success;
    if (score >= 60) return colors.accent.warning;
    return colors.accent.danger;
  };

  const getNQCCategory = (score) => {
    if (score >= 80) return 'GOOD';
   if (score >= 60) return 'MODERATE';
    return 'POOR';
  };

  return (
    <Card padding="lg" role="region" aria-label="NQC Score">
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
          NARRATIVE–QUANTITATIVE COHERENCE
        </div>
        <div style={{ 
          fontSize: typography.fontSize['4xl'], 
          fontWeight: 700, 
          color: getNQCColor(nqcScore),
          marginBottom: spacing.sm 
        }}>
          {nqcScore.toFixed(0)}
        </div>
        <Badge
          variant={nqcScore >= 80 ? 'success' : nqcScore >= 60 ? 'warning' : 'danger'}
          size="md"
          aria-label={`NQC category: ${getNQCCategory(nqcScore)}`}
        >
          {getNQCCategory(nqcScore)}
        </Badge>
        {confidence && (
          <div style={{ 
            marginTop: spacing.sm, 
            fontSize: typography.fontSize.sm, 
            color: colors.text.secondary 
          }}>
            Confidence: {confidence}
          </div>
        )}
      </div>
    </Card>
  );
}

export default memo(NQCGauge);
