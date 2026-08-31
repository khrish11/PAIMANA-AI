import React, { useState } from 'react';
import { colors, spacing, typography } from '../../tokens';

function PlaybookCard({
  playbook,
  triggerReason,
  onDismiss,
  onViewed,
  isSuggestion = false,
  loading = false,
  error = null,
}) {
  const [expanded, setExpanded] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  if (loading) {
    return (
      <div style={{ padding: spacing.lg, textAlign: 'center', color: colors.text.muted }}>
        Loading playbook...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: spacing.lg, textAlign: 'center', color: colors.accent.danger }}>
        {error}
      </div>
    );
  }

  if (!playbook) {
    return null;
  }

  const getConfidenceColor = (tier) => {
    switch (tier) {
      case 'HIGH': return colors.accent.success;
      case 'MEDIUM': return colors.accent.warning;
      case 'LOW': return colors.accent.danger;
      default: return colors.text.muted;
    }
  };

  const handleDismiss = async () => {
    if (onDismiss) {
      await onDismiss(playbook.suggestion_id || playbook.playbook_id);
      setDismissed(true);
    }
  };

  const handleViewed = async () => {
    if (onViewed) {
      await onViewed(playbook.suggestion_id || playbook.playbook_id);
    }
    setExpanded(!expanded);
  };

  if (dismissed) {
    return null;
  }

  return (
    <div style={{
      padding: spacing.lg,
      backgroundColor: colors.background.secondary,
      borderRadius: '0.5rem',
      border: `1px solid ${colors.border.light}`,
      marginBottom: spacing.md,
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: spacing.md,
      }}>
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: typography.fontSize.sm,
            color: colors.text.muted,
            marginBottom: spacing.xs,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}>
            {playbook.category.replace('_', ' ')}
          </div>
          <h3 style={{
            fontSize: typography.fontSize.lg,
            fontWeight: 600,
            color: colors.text.primary,
            marginBottom: spacing.sm,
          }}>
            &ldquo;{playbook.label}&rdquo;
          </h3>
          <div style={{
            display: 'flex',
            gap: spacing.sm,
            alignItems: 'center',
          }}>
            <span style={{
              fontSize: typography.fontSize.sm,
              fontWeight: 600,
              color: getConfidenceColor(playbook.confidence_tier),
              padding: `${spacing.xs} ${spacing.sm}`,
              backgroundColor: `${getConfidenceColor(playbook.confidence_tier)}15`,
              borderRadius: '0.25rem',
            }}>
              {playbook.confidence_tier} CONFIDENCE
            </span>
            <span style={{
              fontSize: typography.fontSize.sm,
              color: colors.text.secondary,
            }}>
              Used successfully in {playbook.source_project_count} comparable projects
            </span>
          </div>
        </div>
        {isSuggestion && (
          <button
            onClick={handleDismiss}
            style={{
              padding: `${spacing.xs} ${spacing.sm}`,
              fontSize: typography.fontSize.sm,
              color: colors.text.muted,
              backgroundColor: 'transparent',
              border: `1px solid ${colors.border.light}`,
              borderRadius: '0.25rem',
              cursor: 'pointer',
              marginLeft: spacing.md,
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = colors.border.light;
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'transparent';
            }}
          >
            Dismiss
          </button>
        )}
      </div>

      {/* Why Recommended */}
      {triggerReason && (
        <div style={{
          padding: spacing.md,
          backgroundColor: `${colors.accent.primary}10`,
          borderRadius: '0.375rem',
          marginBottom: spacing.md,
          borderLeft: `3px solid ${colors.accent.primary}`,
        }}>
          <div style={{
            fontSize: typography.fontSize.sm,
            fontWeight: 600,
            color: colors.text.primary,
            marginBottom: spacing.xs,
          }}>
            Why recommended:
          </div>
          <div style={{
            fontSize: typography.fontSize.sm,
            color: colors.text.secondary,
          }}>
            {triggerReason}
          </div>
        </div>
      )}

      {/* Expand/Collapse Button */}
      <button
        onClick={handleViewed}
        style={{
          width: '100%',
          padding: spacing.sm,
          fontSize: typography.fontSize.sm,
          color: colors.accent.primary,
          backgroundColor: 'transparent',
          border: `1px solid ${colors.accent.primary}30`,
          borderRadius: '0.25rem',
          cursor: 'pointer',
          marginBottom: expanded ? spacing.md : 0,
        }}
        onMouseEnter={(e) => {
          e.target.style.backgroundColor = `${colors.accent.primary}10`;
        }}
        onMouseLeave={(e) => {
          e.target.style.backgroundColor = 'transparent';
        }}
      >
        {expanded ? 'Hide Evidence' : 'View Evidence'}
      </button>

      {/* Evidence Section */}
      {expanded && playbook.evidence_actions && playbook.evidence_actions.length > 0 && (
        <div style={{
          marginTop: spacing.md,
          paddingTop: spacing.md,
          borderTop: `1px solid ${colors.border.light}`,
        }}>
          <div style={{
            fontSize: typography.fontSize.sm,
            fontWeight: 600,
            color: colors.text.primary,
            marginBottom: spacing.sm,
          }}>
            Evidence:
          </div>
          {playbook.evidence_actions.map((action, index) => (
            <div
              key={action.action_id || index}
              style={{
                padding: spacing.sm,
                backgroundColor: colors.background.tertiary,
                borderRadius: '0.25rem',
                marginBottom: spacing.sm,
                borderLeft: `2px solid ${colors.accent.primary}`,
              }}
            >
              {action.quote_evidence && (
                <div style={{
                  fontSize: typography.fontSize.sm,
                  color: colors.text.secondary,
                  fontStyle: 'italic',
                  marginBottom: spacing.xs,
                }}>
                  &ldquo;{action.quote_evidence}&rdquo;
                </div>
              )}
              <div style={{
                fontSize: typography.fontSize.xs,
                color: colors.text.muted,
              }}>
                Source: {action.source_month} • Specificity: {action.specificity_score}/5
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PlaybookCard;
