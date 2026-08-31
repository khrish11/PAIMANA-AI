import { Badge, Button } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';
import { memo } from 'react';

function IntelligenceHeader({ 
  title, 
  subtitle, 
  status, 
  timestamp, 
  confidence, 
  actions = [],
  onWhyClick 
}) {
  return (
    <div style={{ 
      padding: spacing.lg, 
      backgroundColor: colors.background.secondary, 
      borderRadius: borderRadius.lg,
      border: `1px solid ${colors.border.default}`
    }}
    role="region"
    aria-label="Project intelligence header"
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: spacing.md }}>
        <div>
          <h1 style={{ 
            fontSize: typography.fontSize['3xl'], 
            fontWeight: 700, 
            color: colors.text.primary, 
            marginBottom: spacing.sm 
          }}>
            {title}
          </h1>
          {subtitle && (
            <p style={{ 
              fontSize: typography.fontSize.base, 
              color: colors.text.secondary 
            }}>
              {subtitle}
            </p>
          )}
        </div>
        
        <div style={{ display: 'flex', gap: spacing.sm, alignItems: 'center' }}>
          {status && (
            <Badge
              variant={
                status === 'CRITICAL' ? 'critical' :
                status === 'VERY_HIGH' ? 'danger' :
                status === 'HIGH' ? 'warning' :
                status === 'MODERATE' ? 'info' : 'success'
              }
              size="md"
              aria-label={`Risk status: ${status}`}
            >
              {status}
            </Badge>
          )}
          
          {confidence !== undefined && (
            <div 
              style={{ 
                padding: `${spacing.xs} ${spacing.sm}`,
                backgroundColor: colors.background.tertiary,
                borderRadius: borderRadius.sm,
                fontSize: typography.fontSize.sm,
                color: colors.text.secondary
              }}
              aria-label={`Data confidence: ${confidence?.toFixed(0)} percent`}
            >
              Confidence: {confidence?.toFixed(0) || 'N/A'}
            </div>
          )}
          
          {onWhyClick && (
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={onWhyClick}
              aria-label="View risk explanation"
            >
              Why?
            </Button>
          )}
        </div>
      </div>

      {timestamp && (
        <div style={{ 
          fontSize: typography.fontSize.sm, 
          color: colors.text.muted 
        }}>
          Last updated: {new Date(timestamp).toLocaleString() || 'N/A'}
        </div>
      )}

      {actions.length > 0 && (
        <div style={{ 
          marginTop: spacing.md, 
          display: 'flex', 
          gap: spacing.sm, 
          flexWrap: 'wrap' 
        }}>
          {actions.map((action, index) => (
            <Button
              key={index}
              variant={action.variant || 'secondary'}
              size={action.size || 'sm'}
              onClick={action.onClick}
              disabled={action.disabled}
              aria-label={action.label}
            >
              {action.label}
            </Button>
          ))}
        </div>
      )}
    </div>
  );
}

export default memo(IntelligenceHeader);
