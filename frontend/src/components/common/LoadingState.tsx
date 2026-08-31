import React from 'react';
import { colors, spacing, typography } from '../../tokens';

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading...',
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
        gap: spacing.lg,
      }}
    >
      <div
        style={{
          width: '48px',
          height: '48px',
          border: `3px solid ${colors.border.light}`,
          borderTop: `3px solid ${colors.accent.primary}`,
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        }}
      />
      <p
        style={{
          fontFamily: typography.fontFamily.sans,
          fontSize: typography.fontSize.base,
          color: colors.text.secondary,
          margin: 0,
        }}
      >
        {message}
      </p>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
