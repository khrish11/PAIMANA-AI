import { colors, spacing, typography, borderRadius } from '../../tokens';
import { memo } from 'react';

function EvidenceMetadata({ 
  source, 
  updated, 
  model, 
  dataset, 
  confidence,
  predictionTimestamp,
  lastDataUpdate 
}) {
  return (
    <div style={{ 
      padding: spacing.md, 
      backgroundColor: colors.background.tertiary, 
      borderRadius: borderRadius.sm,
      border: `1px solid ${colors.border.light}`
    }}>
      <div style={{ 
        fontSize: typography.fontSize.xs, 
        fontWeight: 600, 
        color: colors.text.muted, 
        marginBottom: spacing.sm,
        textTransform: 'uppercase',
        letterSpacing: '0.05em'
      }}>
        Evidence Metadata
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xs }}>
        {source && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            fontSize: typography.fontSize.xs,
            color: colors.text.secondary
          }}>
            <span>Source:</span>
            <span style={{ fontWeight: 600, color: colors.text.primary }}>{source}</span>
          </div>
        )}
        
        {updated && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            fontSize: typography.fontSize.xs,
            color: colors.text.secondary
          }}>
            <span>Updated:</span>
            <span style={{ fontWeight: 600, color: colors.text.primary }}>
              {new Date(updated).toLocaleString() || 'N/A'}
            </span>
          </div>
        )}
        
        {model && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            fontSize: typography.fontSize.xs,
            color: colors.text.secondary
          }}>
            <span>Model:</span>
            <span style={{ fontWeight: 600, color: colors.text.primary }}>{model}</span>
          </div>
        )}
        
        {dataset && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            fontSize: typography.fontSize.xs,
            color: colors.text.secondary
          }}>
            <span>Dataset:</span>
            <span style={{ fontWeight: 600, color: colors.text.primary }}>{dataset}</span>
          </div>
        )}
        
        {predictionTimestamp && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            fontSize: typography.fontSize.xs,
            color: colors.text.secondary
          }}>
            <span>Predicted:</span>
            <span style={{ fontWeight: 600, color: colors.text.primary }}>
              {new Date(predictionTimestamp).toLocaleString() || 'N/A'}
            </span>
          </div>
        )}
        
        {lastDataUpdate && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            fontSize: typography.fontSize.xs,
            color: colors.text.secondary
          }}>
            <span>Data Update:</span>
            <span style={{ fontWeight: 600, color: colors.text.primary }}>
              {new Date(lastDataUpdate).toLocaleString() || 'N/A'}
            </span>
          </div>
        )}
        
        {confidence !== undefined && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            fontSize: typography.fontSize.xs,
            color: colors.text.secondary
          }}>
            <span>Confidence:</span>
            <span style={{ 
              fontWeight: 600, 
              color: confidence >= 80 ? colors.accent.success : 
                     confidence >= 60 ? colors.accent.warning : 
                     colors.accent.danger 
            }}>
              {confidence?.toFixed(0) || 'N/A'}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export default memo(EvidenceMetadata);
