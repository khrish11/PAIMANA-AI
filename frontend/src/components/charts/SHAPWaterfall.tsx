import React from 'react';
import { colors, spacing, typography, borderRadius } from '../../tokens';

interface SHAPValue {
  feature: string;
  value: number;
  contribution: number;
  direction: 'positive' | 'negative';
  explanation?: string;
}

interface SHAPWaterfallProps {
  values: SHAPValue[];
  baseValue: number;
  finalValue: number;
  className?: string;
}

export const SHAPWaterfall: React.FC<SHAPWaterfallProps> = ({
  values,
  baseValue,
  finalValue,
  className = '',
}) => {
  const maxContribution = Math.max(...values.map((v) => Math.abs(v.contribution)));
  const barWidth = (contribution: number) => (Math.abs(contribution) / maxContribution) * 100;

  return (
    <div className={className} style={{ width: '100%' }}>
      <h4
        style={{
          fontFamily: typography.fontFamily.sans,
          fontSize: typography.fontSize.base,
          fontWeight: typography.fontWeight.semibold as number,
          color: colors.text.primary,
          margin: `0 0 ${spacing.lg} 0`,
        }}
      >
        Why is this project at risk?
      </h4>
      
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: spacing.sm,
        }}
      >
        {/* Base value */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: spacing.md,
          }}
        >
          <div
            style={{
              width: '120px',
              fontSize: typography.fontSize.sm,
              color: colors.text.secondary,
            }}
          >
            Base Value
          </div>
          <div
            style={{
              width: '100px',
              textAlign: 'right',
              fontSize: typography.fontSize.sm,
              fontWeight: typography.fontWeight.medium as number,
              color: colors.text.primary,
            }}
          >
            {baseValue.toFixed(2)}
          </div>
          <div
            style={{
              flex: 1,
              height: '24px',
              backgroundColor: colors.border.light,
              borderRadius: borderRadius.sm,
            }}
          />
        </div>

        {/* SHAP values */}
        {values.slice(0, 5).map((item, index) => (
          <div
            key={index}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: spacing.md,
            }}
          >
            <div
              style={{
                width: '120px',
                fontSize: typography.fontSize.sm,
                color: colors.text.secondary,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
              title={item.feature}
            >
              {item.feature}
            </div>
            <div
              style={{
                width: '100px',
                textAlign: 'right',
                fontSize: typography.fontSize.sm,
                fontWeight: typography.fontWeight.medium as number,
                color: item.direction === 'positive' ? colors.accent.danger : colors.accent.success,
              }}
            >
              {item.contribution > 0 ? '+' : ''}{item.contribution.toFixed(2)}
            </div>
            <div
              style={{
                flex: 1,
                height: '24px',
                backgroundColor: item.direction === 'positive' ? colors.accent.danger : colors.accent.success,
                borderRadius: borderRadius.sm,
                width: `${barWidth(item.contribution)}%`,
                minWidth: '4px',
              }}
            />
          </div>
        ))}

        {/* Final value */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: spacing.md,
            marginTop: spacing.sm,
            paddingTop: spacing.sm,
            borderTop: `1px solid ${colors.border.default}`,
          }}
        >
          <div
            style={{
              width: '120px',
              fontSize: typography.fontSize.sm,
              fontWeight: typography.fontWeight.semibold as number,
              color: colors.text.primary,
            }}
          >
            Final Value
          </div>
          <div
            style={{
              width: '100px',
              textAlign: 'right',
              fontSize: typography.fontSize.sm,
              fontWeight: typography.fontWeight.bold as number,
              color: colors.text.primary,
            }}
          >
            {finalValue.toFixed(2)}
          </div>
          <div
            style={{
              flex: 1,
              height: '24px',
              backgroundColor: colors.accent.primary,
              borderRadius: borderRadius.sm,
            }}
          />
        </div>
      </div>
    </div>
  );
};
