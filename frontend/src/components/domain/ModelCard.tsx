import React from 'react';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';

interface ModelCardProps {
  name: string;
  version: string;
  status: 'experimental' | 'production' | 'deprecated';
  metrics: {
    precision?: number;
    recall?: number;
    f1?: number;
    rocAuc?: number;
  };
  className?: string;
}

export const ModelCard: React.FC<ModelCardProps> = ({
  name,
  version,
  status,
  metrics,
  className = '',
}) => {
  const getStatusVariant = (): 'default' | 'success' | 'warning' | 'danger' | 'critical' | 'info' => {
    switch (status) {
      case 'production':
        return 'success';
      case 'experimental':
        return 'warning';
      case 'deprecated':
        return 'danger';
      default:
        return 'default';
    }
  };

  return (
    <Card className={className} padding="lg" hover={true}>
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: spacing.md,
        }}
      >
        <div>
          <h3
            style={{
              fontFamily: typography.fontFamily.sans,
              fontSize: typography.fontSize.lg,
              fontWeight: typography.fontWeight.semibold as number,
              color: colors.text.primary,
              margin: `0 0 ${spacing.xs} 0`,
            }}
          >
            {name}
          </h3>
          <div
            style={{
              fontFamily: typography.fontFamily.sans,
              fontSize: typography.fontSize.sm,
              color: colors.text.secondary,
            }}
          >
            {version}
          </div>
        </div>
        <Badge variant={getStatusVariant()}>{status}</Badge>
      </div>

      {status === 'experimental' && (
        <div
          style={{
            padding: spacing.sm,
            backgroundColor: `${colors.accent.warning}10`,
            borderRadius: borderRadius.sm,
            marginBottom: spacing.md,
            border: `1px solid ${colors.accent.warning}30`,
          }}
        >
          <div
            style={{
              fontFamily: typography.fontFamily.sans,
              fontSize: typography.fontSize.xs,
              fontWeight: typography.fontWeight.semibold as number,
              color: colors.accent.warning,
              marginBottom: spacing.xs,
            }}
          >
            EXPERIMENTAL MODEL
          </div>
          <div
            style={{
              fontFamily: typography.fontFamily.sans,
              fontSize: typography.fontSize.xs,
              color: colors.text.secondary,
            }}
          >
            Trained on 454 completed projects (v2). Not production validated.
          </div>
        </div>
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: spacing.sm,
        }}
      >
        {metrics.precision !== undefined && (
          <div>
            <div
              style={{
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.xs,
                color: colors.text.muted,
                marginBottom: spacing.xs,
              }}
            >
              Precision
            </div>
            <div
              style={{
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.base,
                fontWeight: typography.fontWeight.medium as number,
                color: colors.text.primary,
              }}
            >
              {(metrics.precision * 100).toFixed(1)}%
            </div>
          </div>
        )}
        {metrics.recall !== undefined && (
          <div>
            <div
              style={{
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.xs,
                color: colors.text.muted,
                marginBottom: spacing.xs,
              }}
            >
              Recall
            </div>
            <div
              style={{
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.base,
                fontWeight: typography.fontWeight.medium as number,
                color: colors.text.primary,
              }}
            >
              {(metrics.recall * 100).toFixed(1)}%
            </div>
          </div>
        )}
        {metrics.f1 !== undefined && (
          <div>
            <div
              style={{
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.xs,
                color: colors.text.muted,
                marginBottom: spacing.xs,
              }}
            >
              F1 Score
            </div>
            <div
              style={{
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.base,
                fontWeight: typography.fontWeight.medium as number,
                color: colors.text.primary,
              }}
            >
              {metrics.f1.toFixed(3)}
            </div>
          </div>
        )}
        {metrics.rocAuc !== undefined && (
          <div>
            <div
              style={{
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.xs,
                color: colors.text.muted,
                marginBottom: spacing.xs,
              }}
            >
              ROC-AUC
            </div>
            <div
              style={{
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.base,
                fontWeight: typography.fontWeight.medium as number,
                color: colors.text.primary,
              }}
            >
              {metrics.rocAuc.toFixed(3)}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};
