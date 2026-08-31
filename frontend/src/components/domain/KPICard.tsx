import React from 'react';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { Card } from '../common/Card';

interface KPICardProps {
  label: string;
  value: string | number;
  trend?: string;
  trendDirection?: 'up' | 'down' | 'neutral';
  icon?: string;
  className?: string;
}

export const KPICard: React.FC<KPICardProps> = ({
  label,
  value,
  trend,
  trendDirection = 'neutral',
  icon,
  className = '',
}) => {
  const getTrendColor = () => {
    if (trendDirection === 'up') return colors.accent.success;
    if (trendDirection === 'down') return colors.accent.danger;
    return colors.text.secondary;
  };

  return (
    <Card className={className} padding="lg" hover={false}>
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: spacing.sm,
        }}
      >
        {icon && (
          <div
            style={{
              fontSize: typography.fontSize.xl,
            }}
          >
            {icon}
          </div>
        )}
        {trend && (
          <div
            style={{
              fontSize: typography.fontSize.xs,
              fontWeight: typography.fontWeight.medium as number,
              color: getTrendColor(),
              display: 'flex',
              alignItems: 'center',
              gap: spacing.xs,
            }}
          >
            {trendDirection === 'up' && '↑'}
            {trendDirection === 'down' && '↓'}
            {trend}
          </div>
        )}
      </div>
      <div
        style={{
          fontFamily: typography.fontFamily.sans,
          fontSize: typography.fontSize['3xl'],
          fontWeight: typography.fontWeight.bold as number,
          color: colors.text.primary,
          lineHeight: 1,
          marginBottom: spacing.xs,
        }}
      >
        {value}
      </div>
      <div
        style={{
          fontFamily: typography.fontFamily.sans,
          fontSize: typography.fontSize.sm,
          color: colors.text.secondary,
        }}
      >
        {label}
      </div>
    </Card>
  );
};
