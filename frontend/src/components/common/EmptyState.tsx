import React from 'react';
import { colors, spacing, typography } from '../../tokens';

interface EmptyStateProps {
  icon?: string;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon = '📭',
  title,
  description,
  action,
  className = '',
}) => {
  return (
    <div
      className={className}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: spacing['3xl'],
        textAlign: 'center',
      }}
    >
      <div
        style={{
          fontSize: '4rem',
          marginBottom: spacing.lg,
        }}
      >
        {icon}
      </div>
      <h3
        style={{
          fontFamily: typography.fontFamily.sans,
          fontSize: typography.fontSize.xl,
          fontWeight: typography.fontWeight.semibold as number,
          color: colors.text.primary,
          margin: `0 0 ${spacing.sm} 0`,
        }}
      >
        {title}
      </h3>
      {description && (
        <p
          style={{
            fontFamily: typography.fontFamily.sans,
            fontSize: typography.fontSize.base,
            color: colors.text.secondary,
            margin: `0 0 ${spacing.xl} 0`,
            maxWidth: '400px',
          }}
        >
          {description}
        </p>
      )}
      {action}
    </div>
  );
};
