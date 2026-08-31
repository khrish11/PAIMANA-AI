import React from 'react';
import { colors, spacing, typography } from '../../tokens';

interface DataPoint {
  date: string;
  compositeRisk: number;
  costRisk: number;
  scheduleRisk: number;
  progressAnomaly: number;
  dcs: number;
}

interface RiskTrendProps {
  data: DataPoint[];
  className?: string;
}

export const RiskTrend: React.FC<RiskTrendProps> = ({ data, className = '' }) => {
  const maxValue = Math.max(
    ...data.flatMap((d) => [d.compositeRisk, d.costRisk, d.scheduleRisk, d.progressAnomaly])
  );

  const getX = (index: number) => (index / (data.length - 1)) * 100;
  const getY = (value: number) => 100 - (value / maxValue) * 100;

  const createPath = (key: keyof DataPoint, color: string) => {
    const points = data.map((d, i) => `${getX(i)},${getY(d[key])}`).join(' ');
    return points;
  };

  return (
    <div className={className} style={{ width: '100%', height: '300px' }}>
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        style={{ display: 'block' }}
      >
        {/* Grid lines */}
        {[0, 25, 50, 75, 100].map((y) => (
          <line
            key={y}
            x1="0"
            y1={y}
            x2="100"
            y2={y}
            stroke={colors.border.light}
            strokeWidth="0.5"
          />
        ))}

        {/* Risk lines */}
        <polyline
          points={createPath('compositeRisk', colors.accent.primary)}
          fill="none"
          stroke={colors.accent.primary}
          strokeWidth="2"
        />
        <polyline
          points={createPath('costRisk', colors.accent.warning)}
          fill="none"
          stroke={colors.accent.warning}
          strokeWidth="1.5"
        />
        <polyline
          points={createPath('scheduleRisk', colors.accent.info)}
          fill="none"
          stroke={colors.accent.info}
          strokeWidth="1.5"
        />
        <polyline
          points={createPath('progressAnomaly', colors.accent.secondary)}
          fill="none"
          stroke={colors.accent.secondary}
          strokeWidth="1.5"
        />
      </svg>

      {/* Legend */}
      <div
        style={{
          display: 'flex',
          gap: spacing.lg,
          marginTop: spacing.md,
          flexWrap: 'wrap',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: spacing.xs,
            fontSize: typography.fontSize.xs,
            color: colors.text.secondary,
          }}
        >
          <div
            style={{
              width: '12px',
              height: '2px',
              backgroundColor: colors.accent.primary,
            }}
          />
          Composite Risk
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: spacing.xs,
            fontSize: typography.fontSize.xs,
            color: colors.text.secondary,
          }}
        >
          <div
            style={{
              width: '12px',
              height: '2px',
              backgroundColor: colors.accent.warning,
            }}
          />
          Cost Risk
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: spacing.xs,
            fontSize: typography.fontSize.xs,
            color: colors.text.secondary,
          }}
        >
          <div
            style={{
              width: '12px',
              height: '2px',
              backgroundColor: colors.accent.info,
            }}
          />
          Schedule Risk
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: spacing.xs,
            fontSize: typography.fontSize.xs,
            color: colors.text.secondary,
          }}
        >
          <div
            style={{
              width: '12px',
              height: '2px',
              backgroundColor: colors.accent.secondary,
            }}
          />
          Progress Anomaly
        </div>
      </div>
    </div>
  );
};
