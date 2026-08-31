import React from 'react';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';

interface AnomalyCardProps {
  severity: 'low' | 'medium' | 'high' | 'critical';
  type: string;
  observed: number;
  expected: number;
  delta: number;
  explanation: string;
  month: string;
  className?: string;
}

export const AnomalyCard: React.FC<AnomalyCardProps> = ({
  severity,
  type,
  observed,
  expected,
  delta,
  explanation,
  month,
  className = '',
}) => {
  const getSeverityVariant = (): 'default' | 'success' | 'warning' | 'danger' | 'critical' | 'info' => {
    switch (severity) {
      case 'critical':
        return 'critical';
      case 'high':
        return 'danger';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Card className={className} padding="md" hover={false}>
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: spacing.sm,
        }}
      >
        <div
          style={{
            fontFamily: typography.fontFamily.sans,
            fontSize: typography.fontSize.sm,
            fontWeight: typography.fontWeight.semibold as number,
            color: colors.text.primary,
          }}
        >
          {type}
        </div>
        <Badge variant={getSeverityVariant()} size="sm">
          {severity}
        </Badge>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: spacing.sm,
          marginBottom: spacing.sm,
        }}
      >
        <div>
          <div
            style={{
              fontFamily: typography.fontFamily.sans,
              fontSize: typography.fontSize.xs,
              color: colors.text.muted,
              marginBottom: spacing.xs,
            }}
          >
            Observed
          </div>
          <div
            style={{
              fontFamily: typography.fontFamily.sans,
              fontSize: typography.fontSize.base,
              fontWeight: typography.fontWeight.medium as number,
              color: colors.text.primary,
            }}
          >
            {observed.toFixed(2)}
          </div>
        </div>
        <div>
          <div
            style={{
              fontFamily: typography.fontFamily.sans,
              fontSize: typography.fontSize.xs,
              color: colors.text.muted,
              marginBottom: spacing.xs,
            }}
          >
            Expected
          </div>
          <div
            style={{
              fontFamily: typography.fontFamily.sans,
              fontSize: typography.fontSize.base,
              fontWeight: typography.fontWeight.medium as number,
              color: colors.text.primary,
            }}
          >
            {expected.toFixed(2)}
          </div>
        </div>
        <div>
          <div
            style={{
              fontFamily: typography.fontFamily.sans,
              fontSize: typography.fontSize.xs,
              color: colors.text.muted,
              marginBottom: spacing.xs,
            }}
          >
            Delta
          </div>
          <div
            style={{
              fontFamily: typography.fontFamily.sans,
              fontSize: typography.fontSize.base,
              fontWeight: typography.fontWeight.medium as number,
              color: delta > 0 ? colors.accent.danger : colors.accent.success,
            }}
          >
            {delta > 0 ? '+' : ''}{delta.toFixed(2)}
          </div>
        </div>
      </div>

      <div
        style={{
          fontFamily: typography.fontFamily.sans,
          fontSize: typography.fontSize.sm,
          color: colors.text.secondary,
          marginBottom: spacing.sm,
        }}
      >
        {explanation}
      </div>

      <div
        style={{
          fontFamily: typography.fontFamily.sans,
          fontSize: typography.fontSize.xs,
          color: colors.text.muted,
        }}
      >
        {month}
      </div>
    </Card>
  );
};
