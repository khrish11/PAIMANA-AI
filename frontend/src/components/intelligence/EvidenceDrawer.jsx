import { Card, Badge, Button } from '../common';
import { colors, spacing, typography, borderRadius, shadows, transitions } from '../../tokens';

function EvidenceDrawer({ isOpen, onClose, evidence }) {
  if (!isOpen || !evidence) return null;

  return (
    <div 
      style={{
        position: 'fixed',
        top: 0,
        right: 0,
        width: '100%',
        maxWidth: '500px',
        height: '100%',
        backgroundColor: colors.background.primary,
        boxShadow: shadows.xl,
        zIndex: 1050,
        transform: isOpen ? 'translateX(0)' : 'translateX(100%)',
        transition: transitions.normal,
        overflow: 'auto',
        padding: spacing.xl,
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="evidence-drawer-title"
    >
      <div style={{ padding: spacing.lg, borderBottom: `1px solid ${colors.border.default}` }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 id="evidence-drawer-title" style={{ fontSize: typography.fontSize.xl, fontWeight: 700, color: colors.text.primary }}>
            Risk Evidence
          </h2>
          <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close evidence drawer">
            ✕
          </Button>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: spacing.lg }}>
        {evidence ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
            {/* Risk Score */}
            <Card padding="md">
              <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
                Composite Risk Score
              </div>
              <div style={{ fontSize: typography.fontSize['3xl'], fontWeight: 700, color: colors.text.primary }}>
                {evidence.risk_score || 'N/A'}
              </div>
              <Badge
                variant={
                  evidence.risk_category === 'CRITICAL' ? 'critical' :
                  evidence.risk_category === 'VERY_HIGH' ? 'danger' :
                  evidence.risk_category === 'HIGH' ? 'warning' :
                  evidence.risk_category === 'MODERATE' ? 'info' : 'success'
                }
                size="md"
                style={{ marginTop: spacing.sm }}
              >
                {evidence.risk_category || 'N/A'}
              </Badge>
            </Card>

            {/* Confidence */}
            <Card padding="md">
              <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
                Confidence
              </div>
              <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 600, color: colors.text.primary }}>
                {evidence.confidence || 'N/A'}
              </div>
            </Card>

            {/* Top Risk Drivers */}
            {evidence.shap_drivers && evidence.shap_drivers.length > 0 && (
              <Card padding="md">
                <div style={{ marginBottom: spacing.md, fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
                  Top Risk Drivers
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
                  {evidence.shap_drivers.slice(0, 5).map((driver, index) => (
                    <div
                      key={index}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        padding: spacing.sm,
                        backgroundColor: colors.background.tertiary,
                        borderRadius: borderRadius.sm,
                      }}
                    >
                      <span style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
                        {driver.human_label || driver.feature}
                      </span>
                      <span style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.primary }}>
                        {driver.contribution ? driver.contribution.toFixed(2) : 'N/A'}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Explanation */}
            {evidence.explanation && (
              <Card padding="md">
                <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
                  Explanation
                </div>
                <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, lineHeight: 1.6 }}>
                  {evidence.explanation}
                </div>
              </Card>
            )}

            {/* Supporting Data */}
            {evidence.supporting_data && (
              <Card padding="md">
                <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
                  Supporting Data
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xs }}>
                  {Object.entries(evidence.supporting_data).map(([key, value]) => (
                    <div key={key} style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
                        {key}
                      </span>
                      <span style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.primary }}>
                        {value}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Metadata */}
            <Card padding="md">
              <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
                Metadata
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xs }}>
                <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>
                  Timestamp: {evidence.timestamp || 'N/A'}
                </div>
                <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>
                  Model Version: {evidence.model_version || 'N/A'}
                </div>
              </div>
            </Card>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: spacing.xl, color: colors.text.muted }}>
            No evidence available
          </div>
        )}
      </div>

      <div style={{ padding: spacing.lg, borderTop: `1px solid ${colors.border.default}` }}>
        <Button variant="primary" onClick={onClose} style={{ width: '100%' }}>
          Close
        </Button>
      </div>
    </div>
  );
}

export default EvidenceDrawer;
