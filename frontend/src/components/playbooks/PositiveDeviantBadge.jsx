import React from 'react';
import { colors, spacing, typography } from '../../tokens';

function PositiveDeviantBadge({ deviant, onClick, dataConfidenceScore }) {
  const getBadgeColor = () => {
    const score = dataConfidenceScore ?? deviant?.data_confidence_score ?? 0;
    if (score >= 80) return colors.accent.success;
    if (score >= 70) return colors.accent.warning;
    return colors.accent.danger;
  };

  return (
    <div
      onClick={onClick}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: spacing.sm,
        padding: `${spacing.xs} ${spacing.sm}`,
        backgroundColor: `${getBadgeColor()}15`,
        border: `1px solid ${getBadgeColor()}40`,
        borderRadius: '9999px',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s ease',
      }}
      onMouseEnter={(e) => {
        if (onClick) {
          e.target.style.backgroundColor = `${getBadgeColor()}25`;
          e.target.style.borderColor = getBadgeColor();
        }
      }}
      onMouseLeave={(e) => {
        if (onClick) {
          e.target.style.backgroundColor = `${getBadgeColor()}15`;
          e.target.style.borderColor = `${getBadgeColor()}40`;
        }
      }}
    >
      <div style={{
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        backgroundColor: getBadgeColor(),
      }} />
      <span style={{
        fontSize: typography.fontSize.xs,
        fontWeight: 600,
        color: getBadgeColor(),
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
      }}>
        Positive Deviant
      </span>
    </div>
  );
}

export default PositiveDeviantBadge;
