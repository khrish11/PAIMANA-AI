import React from 'react';
import { colors, borderRadius, spacing, shadows } from '../../tokens';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: keyof typeof spacing;
  hover?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  padding = 'lg',
  hover = false,
}) => {
  return (
    <div
      className={className}
      style={{
        backgroundColor: colors.background.secondary,
        borderRadius: borderRadius.lg,
        padding: spacing[padding],
        boxShadow: shadows.md,
        border: `1px solid ${colors.border.default}`,
        transition: hover ? 'box-shadow 0.2s ease, transform 0.2s ease' : undefined,
        ...(hover && {
          cursor: 'pointer',
        }),
      }}
      onMouseEnter={(e) => {
        if (hover) {
          e.currentTarget.style.boxShadow = shadows.lg;
          e.currentTarget.style.transform = 'translateY(-2px)';
        }
      }}
      onMouseLeave={(e) => {
        if (hover) {
          e.currentTarget.style.boxShadow = shadows.md;
          e.currentTarget.style.transform = 'translateY(0)';
        }
      }}
    >
      {children}
    </div>
  );
};
