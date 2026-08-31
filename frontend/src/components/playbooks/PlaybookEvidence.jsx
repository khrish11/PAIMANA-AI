import React from 'react';
import { colors, spacing, typography } from '../../tokens';

function PlaybookEvidence({ actions, loading }) {
  if (loading) {
    return (
      <div style={{ padding: spacing.lg, textAlign: 'center' }}>
        <div style={{ color: colors.text.muted }}>Loading evidence...</div>
      </div>
    );
  }

  if (!actions || actions.length === 0) {
    return (
      <div style={{ padding: spacing.lg, textAlign: 'center' }}>
        <div style={{ color: colors.text.muted }}>No evidence available</div>
      </div>
    );
  }

  return (
    <div style={{ padding: spacing.lg }}>
      <div style={{
        fontSize: typography.fontSize.base,
        fontWeight: 600,
        color: colors.text.primary,
        marginBottom: spacing.lg,
      }}>
        Evidence from {actions.length} Source Actions
      </div>

      {actions.map((action, index) => (
        <div
          key={action.action_id || index}
          style={{
            padding: spacing.lg,
            backgroundColor: colors.background.secondary,
            borderRadius: '0.5rem',
            border: `1px solid ${colors.border.light}`,
            marginBottom: spacing.md,
          }}
        >
          {/* Action Text */}
          <div style={{
            fontSize: typography.fontSize.base,
            fontWeight: 500,
            color: colors.text.primary,
            marginBottom: spacing.sm,
          }}>
            {action.action_text}
          </div>

          {/* Quote Evidence */}
          {action.quote_evidence && (
            <div style={{
              padding: spacing.md,
              backgroundColor: colors.background.tertiary,
              borderRadius: '0.375rem',
              marginBottom: spacing.sm,
              borderLeft: `3px solid ${colors.accent.primary}`,
            }}>
              <div style={{
                fontSize: typography.fontSize.sm,
                color: colors.text.secondary,
                fontStyle: 'italic',
              }}>
                &ldquo;{action.quote_evidence}&rdquo;
              </div>
            </div>
          )}

          {/* Metadata */}
          <div style={{
            display: 'flex',
            gap: spacing.lg,
            flexWrap: 'wrap',
            fontSize: typography.fontSize.sm,
            color: colors.text.muted,
          }}>
            <div>
              <strong>Category:</strong> {action.category.replace('_', ' ')}
            </div>
            <div>
              <strong>Source Month:</strong> {action.source_month}
            </div>
            <div>
              <strong>Specificity:</strong> {action.specificity_score}/5
            </div>
            {action.llm_model_version && (
              <div>
                <strong>Model:</strong> {action.llm_model_version}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default PlaybookEvidence;
