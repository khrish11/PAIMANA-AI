import React from 'react';
import { colors, borderRadius, spacing, typography, transitions } from '../../tokens';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
  className = '',
  type = 'button',
}) => {
  const baseStyles = {
    fontFamily: typography.fontFamily.sans,
    fontWeight: typography.fontWeight.medium as number,
    borderRadius: borderRadius.md,
    border: 'none',
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: transitions.fast,
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
  };

  const variantStyles = {
    primary: {
      backgroundColor: disabled ? colors.border.light : colors.accent.primary,
      color: colors.text.primary,
    },
    secondary: {
      backgroundColor: disabled ? colors.border.light : colors.accent.secondary,
      color: colors.text.primary,
    },
    danger: {
      backgroundColor: disabled ? colors.border.light : colors.accent.danger,
      color: colors.text.primary,
    },
    ghost: {
      backgroundColor: 'transparent',
      color: disabled ? colors.text.muted : colors.text.secondary,
      border: `1px solid ${colors.border.default}`,
    },
  };

  const sizeStyles = {
    sm: {
      padding: `${spacing.xs} ${spacing.sm}`,
      fontSize: typography.fontSize.sm,
    },
    md: {
      padding: `${spacing.sm} ${spacing.lg}`,
      fontSize: typography.fontSize.base,
    },
    lg: {
      padding: `${spacing.md} ${spacing.xl}`,
      fontSize: typography.fontSize.lg,
    },
  };

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={className}
      style={{
        ...baseStyles,
        ...variantStyles[variant],
        ...sizeStyles[size],
      }}
      onMouseEnter={(e) => {
        if (!disabled && variant !== 'ghost') {
          e.currentTarget.style.opacity = '0.9';
        }
      }}
      onMouseLeave={(e) => {
        if (!disabled && variant !== 'ghost') {
          e.currentTarget.style.opacity = '1';
        }
      }}
    >
      {children}
    </button>
  );
};
