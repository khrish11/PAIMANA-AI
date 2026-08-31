import React from 'react';
import { colors, spacing, typography } from '../../tokens';

interface RiskGaugeProps {
  value: number;
  max?: number;
  label?: string;
  className?: string;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({
  value,
  max = 100,
  label = 'Risk Score',
  className = '',
}) => {
  const percentage = Math.min((value / max) * 100, 100);
  const getColor = (pct: number) => {
    if (pct < 33) return colors.risk.low;
    if (pct < 66) return colors.risk.medium;
    if (pct < 85) return colors.risk.high;
    return colors.risk.critical;
  };

  const gaugeColor = getColor(percentage);

  return (
    <div className={className} style={{ textAlign: 'center' }}>
      <div
        style={{
          position: 'relative',
          width: '200px',
          height: '100px',
          margin: '0 auto',
          overflow: 'hidden',
        }}
      >
        {/* Background arc */}
        <svg
          width="200"
          height="100"
          viewBox="0 0 200 100"
          style={{ display: 'block' }}
        >
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke={colors.border.light}
            strokeWidth="16"
            strokeLinecap="round"
          />
          {/* Value arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke={gaugeColor}
            strokeWidth="16"
            strokeLinecap="round"
            strokeDasharray={`${percentage * 2.51} 251`}
            style={{
              transition: 'stroke-dasharray 0.5s ease',
            }}
          />
        </svg>
      </div>
      <div
        style={{
          marginTop: spacing.sm,
        }}
      >
        <div
          style={{
            fontFamily: typography.fontFamily.sans,
            fontSize: typography.fontSize['3xl'],
            fontWeight: typography.fontWeight.bold as number,
            color: gaugeColor,
            lineHeight: 1,
          }}
        >
          {value.toFixed(1)}
        </div>
        <div
          style={{
            fontFamily: typography.fontFamily.sans,
            fontSize: typography.fontSize.sm,
            color: colors.text.secondary,
            marginTop: spacing.xs,
          }}
        >
          {label}
        </div>
      </div>
    </div>
  );
};
