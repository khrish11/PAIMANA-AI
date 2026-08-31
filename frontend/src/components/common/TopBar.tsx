import React from 'react';
import { colors, spacing, typography, borderRadius } from '../../tokens';

interface TopBarProps {
  title: string;
  className?: string;
}

export const TopBar: React.FC<TopBarProps> = ({ title, className = '' }) => {
  return (
    <header
      className={className}
      style={{
        height: '64px',
        backgroundColor: colors.background.primary,
        borderBottom: `1px solid ${colors.border.default}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: `0 ${spacing.xl}`,
        position: 'fixed',
        top: 0,
        left: '280px',
        right: 0,
        zIndex: 999,
      }}
    >
      {/* Left: Title */}
      <div>
        <h2
          style={{
            fontFamily: typography.fontFamily.sans,
            fontSize: typography.fontSize.lg,
            fontWeight: typography.fontWeight.semibold as number,
            color: colors.text.primary,
            margin: 0,
          }}
        >
          {title}
        </h2>
      </div>

      {/* Right: Actions */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: spacing.md,
        }}
      >
        {/* Search */}
        <div
          style={{
            position: 'relative',
          }}
        >
          <input
            type="text"
            placeholder="Search..."
            style={{
              width: '200px',
              padding: `${spacing.sm} ${spacing.md}`,
              backgroundColor: colors.background.secondary,
              border: `1px solid ${colors.border.default}`,
              borderRadius: borderRadius.md,
              color: colors.text.primary,
              fontFamily: typography.fontFamily.sans,
              fontSize: typography.fontSize.sm,
              outline: 'none',
            }}
          />
        </div>

        {/* Status Indicators */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: spacing.sm,
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: spacing.xs,
              padding: `${spacing.xs} ${spacing.sm}`,
              backgroundColor: colors.background.secondary,
              borderRadius: borderRadius.sm,
            }}
          >
            <div
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: colors.accent.success,
              }}
            />
            <span
              style={{
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.xs,
                color: colors.text.secondary,
              }}
            >
              ML Active
            </span>
          </div>
        </div>

        {/* Notifications */}
        <button
          style={{
            width: '40px',
            height: '40px',
            backgroundColor: colors.background.secondary,
            border: `1px solid ${colors.border.default}`,
            borderRadius: borderRadius.md,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            color: colors.text.secondary,
            fontSize: typography.fontSize.lg,
          }}
        >
          🔔
        </button>
      </div>
    </header>
  );
};
