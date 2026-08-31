import React from 'react';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { Card } from '../common/Card';

interface DCSCardProps {
  dcs: number;
  trend?: number;
  className?: string;
  components?: {
    completeness?: number;
    freshness?: number;
    consistency?: number;
    reliability?: number;
  };
  confidenceLabel?: string;
  warningFlags?: string[];
}

export const DCSCard: React.FC<DCSCardProps> = ({ dcs, trend, className = '', components, confidenceLabel, warningFlags }) => {
  const getColor = () => {
    if (dcs >= 80) return colors.accent.success;
    if (dcs >= 60) return colors.accent.warning;
    return colors.accent.danger;
  };

  const color = getColor();

  return (
    <Card className={className} padding="lg" hover={false}>
      <div
        style={{
          fontFamily: typography.fontFamily.sans,
          fontSize: typography.fontSize.sm,
          color: colors.text.secondary,
          marginBottom: spacing.sm,
        }}
      >
        Data Completeness Score
      </div>
      <div
        style={{
          display: 'flex',
          alignItems: 'baseline',
          gap: spacing.sm,
          marginBottom: spacing.sm,
        }}
      >
        <div
          style={{
            fontFamily: typography.fontFamily.sans,
            fontSize: typography.fontSize['4xl'],
            fontWeight: typography.fontWeight.bold as number,
            color: color,
            lineHeight: 1,
          }}
        >
          {dcs.toFixed(1)}
        </div>
        <div
          style={{
            fontFamily: typography.fontFamily.sans,
            fontSize: typography.fontSize.xl,
            color: colors.text.muted,
          }}
        >
          /100
        </div>
      </div>

      {/* Progress bar */}
      <div
        style={{
          width: '100%',
          height: '8px',
          backgroundColor: colors.border.light,
          borderRadius: borderRadius.full,
          overflow: 'hidden',
          marginBottom: spacing.sm,
        }}
      >
        <div
          style={{
            width: `${dcs}%`,
            height: '100%',
            backgroundColor: color,
            transition: 'width 0.5s ease',
          }}
        />
      </div>

      {trend !== undefined && (
        <div
          style={{
            fontFamily: typography.fontFamily.sans,
            fontSize: typography.fontSize.xs,
            color: trend > 0 ? colors.accent.success : colors.accent.danger,
          }}
        >
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(1)}% from last month
        </div>
      )}

      {/* DCS Components */}
      {components && (
        <div style={{ marginTop: spacing.md, paddingTop: spacing.md, borderTop: `1px solid ${colors.border.light}` }}>
          <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted, marginBottom: spacing.sm }}>
            Data Quality Dimensions
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: spacing.sm }}>
            {components.completeness !== undefined && (
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.secondary }}>
                Completeness: {components.completeness.toFixed(0)}
              </div>
            )}
            {components.freshness !== undefined && (
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.secondary }}>
                Freshness: {components.freshness.toFixed(0)}
              </div>
            )}
            {components.consistency !== undefined && (
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.secondary }}>
                Consistency: {components.consistency.toFixed(0)}
              </div>
            )}
            {components.reliability !== undefined && (
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.secondary }}>
                Reliability: {components.reliability.toFixed(0)}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Confidence Label */}
      {confidenceLabel && (
        <div style={{ marginTop: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
          {confidenceLabel}
        </div>
      )}

      {/* Warning Flags */}
      {warningFlags && warningFlags.length > 0 && (
        <div style={{ marginTop: spacing.sm }}>
          {warningFlags.map((flag, index) => (
            <div
              key={index}
              style={{
                padding: `${spacing.xs} ${spacing.sm}`,
                backgroundColor: `${colors.accent.warning}10`,
                borderRadius: borderRadius.sm,
                fontSize: typography.fontSize.xs,
                color: colors.text.secondary,
                marginBottom: spacing.xs,
              }}
            >
              ⚠️ {flag}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
