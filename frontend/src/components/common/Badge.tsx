import React from 'react';
import { colors, borderRadius, spacing, typography } from '../../tokens';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'critical' | 'info';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className = '',
}) => {
  const variantStyles = {
    default: {
      backgroundColor: colors.background.tertiary,
      color: colors.text.secondary,
    },
    success: {
      backgroundColor: `${colors.accent.success}20`,
      color: colors.accent.success,
    },
    warning: {
      backgroundColor: `${colors.accent.warning}20`,
      color: colors.accent.warning,
    },
    danger: {
      backgroundColor: `${colors.accent.danger}20`,
      color: colors.accent.danger,
    },
    critical: {
      backgroundColor: `${colors.accent.critical}20`,
      color: colors.accent.critical,
    },
    info: {
      backgroundColor: `${colors.accent.info}20`,
      color: colors.accent.info,
    },
  };

  const sizeStyles = {
    sm: {
      padding: `${spacing.xs} ${spacing.sm}`,
      fontSize: typography.fontSize.xs,
      borderRadius: borderRadius.sm,
    },
    md: {
      padding: `${spacing.xs} ${spacing.md}`,
      fontSize: typography.fontSize.sm,
      borderRadius: borderRadius.md,
    },
  };

  return (
    <span
      className={className}
      style={{
        ...variantStyles[variant],
        ...sizeStyles[size],
        fontFamily: typography.fontFamily.sans,
        fontWeight: typography.fontWeight.medium as number,
        display: 'inline-flex',
        alignItems: 'center',
        whiteSpace: 'nowrap',
      }}
    >
      {children}
    </span>
  );
};
