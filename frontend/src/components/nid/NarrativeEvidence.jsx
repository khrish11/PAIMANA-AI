import { Card } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { memo } from 'react';

function NarrativeEvidence({ narrativeText, highlightedClaim }) {
  if (!narrativeText) {
    return (
      <Card padding="lg" role="region" aria-label="Narrative Evidence">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          No narrative text available
        </div>
      </Card>
    );
  }

  const highlightText = (text, claim) => {
    if (!claim) return text;
    
    // Simple highlight - in production, this would use more sophisticated text matching
    const parts = text.split(new RegExp(`(${claim})`, 'gi'));
    return parts.map((part, index) => 
      part.toLowerCase() === claim.toLowerCase() ? (
        <mark key={index} style={{ 
          backgroundColor: `${colors.accent.warning}30`,
          padding: '2px 4px',
          borderRadius: '2px',
          fontWeight: 600
        }}>
          {part}
        </mark>
      ) : part
    );
  };

  return (
    <Card padding="lg" role="region" aria-label="Narrative Evidence">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Narrative Source
      </h3>

      <div style={{ 
        padding: spacing.md, 
        backgroundColor: colors.background.tertiary, 
        borderRadius: borderRadius.md,
        fontSize: typography.fontSize.base,
        color: colors.text.secondary,
        lineHeight: 1.6,
        maxHeight: '300px',
        overflowY: 'auto'
      }}>
        {highlightText(narrativeText, highlightedClaim)}
      </div>

      {highlightedClaim && (
        <div style={{ marginTop: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
          Highlighted claim: &ldquo;{highlightedClaim}&rdquo;
        </div>
      )}
    </Card>
  );
}

export default memo(NarrativeEvidence);
