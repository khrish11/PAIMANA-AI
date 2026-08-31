import { Card, Badge, Button } from '../common';
import { colors, spacing, typography, borderRadius, shadows } from '../../tokens';
import { memo } from 'react';

function RiskDNA({ riskData, onWhyClick, onComponentClick }) {
  if (!riskData) {
    return (
      <Card padding="lg" role="region" aria-label="Risk DNA">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          Risk DNA unavailable
        </div>
      </Card>
    );
  }

  const getRiskColor = (score) => {
    if (score >= 80) return colors.risk.critical;
    if (score >= 65) return colors.risk.high;
    if (score >= 45) return colors.risk.medium;
    return colors.risk.low;
  };

  const components = riskData.components || {};

  return (
    <Card padding="lg" role="region" aria-label="Project Risk DNA">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.lg }}>
        <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
          Project Risk DNA
        </h3>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={onWhyClick}
          aria-label="View risk explanation"
        >
          Why?
        </Button>
      </div>

      {/* Composite Risk */}
      <div 
        style={{ 
          marginBottom: spacing.xl, 
          padding: spacing.lg, 
          backgroundColor: colors.background.tertiary, 
          borderRadius: borderRadius.md,
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 150ms ease-in-out',
          border: `2px solid ${getRiskColor(riskData.composite_score || 0)}`
        }}
        onClick={() => onComponentClick?.('composite')}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-4px)';
          e.currentTarget.style.boxShadow = shadows.md;
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = 'none';
        }}
        role="button"
        tabIndex={0}
        onKeyPress={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onComponentClick?.('composite');
          }
        }}
        aria-label={`Composite risk score ${riskData.composite_score?.toFixed(1) || 'N/A'}, category ${riskData.risk_category || 'N/A'}`}
      >
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
          COMPOSITE RISK
        </div>
        <div style={{ 
          fontSize: typography.fontSize['4xl'], 
          fontWeight: 700, 
          color: getRiskColor(riskData.composite_score || 0),
          marginBottom: spacing.sm 
        }}>
          {riskData.composite_score?.toFixed(1) || 'N/A'}
        </div>
        <Badge
          variant={
            riskData.risk_category === 'CRITICAL' ? 'critical' :
            riskData.risk_category === 'VERY_HIGH' ? 'danger' :
            riskData.risk_category === 'HIGH' ? 'warning' :
            riskData.risk_category === 'MODERATE' ? 'info' : 'success'
          }
          size="md"
        >
          {riskData.risk_category || 'N/A'}
        </Badge>
      </div>

      {/* Component Risks */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(2, 1fr)', 
        gap: spacing.md 
      }}>
        <div
          style={{
            padding: spacing.md,
            backgroundColor: colors.background.tertiary,
            borderRadius: borderRadius.md,
            cursor: 'pointer',
            transition: 'all 150ms ease-in-out',
            borderLeft: `4px solid ${getRiskColor(components.cost_risk || 0)}`
          }}
          onClick={() => onComponentClick?.('cost_risk')}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateX(4px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateX(0)';
          }}
          role="button"
          tabIndex={0}
          onKeyPress={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onComponentClick?.('cost_risk');
            }
          }}
          aria-label={`Cost risk score ${components.cost_risk?.toFixed(1) || 'N/A'}`}
        >
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            COST RISK
          </div>
          <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
            {components.cost_risk?.toFixed(1) || 'N/A'}
          </div>
        </div>

        <div
          style={{
            padding: spacing.md,
            backgroundColor: colors.background.tertiary,
            borderRadius: borderRadius.md,
            cursor: 'pointer',
            transition: 'all 150ms ease-in-out',
            borderLeft: `4px solid ${getRiskColor(components.schedule_risk || 0)}`
          }}
          onClick={() => onComponentClick?.('schedule_risk')}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateX(4px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateX(0)';
          }}
          role="button"
          tabIndex={0}
          onKeyPress={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onComponentClick?.('schedule_risk');
            }
          }}
          aria-label={`Schedule risk score ${components.schedule_risk?.toFixed(1) || 'N/A'}`}
        >
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            SCHEDULE RISK
          </div>
          <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
            {components.schedule_risk?.toFixed(1) || 'N/A'}
          </div>
        </div>

        <div
          style={{
            padding: spacing.md,
            backgroundColor: colors.background.tertiary,
            borderRadius: borderRadius.md,
            cursor: 'pointer',
            transition: 'all 150ms ease-in-out',
            borderLeft: `4px solid ${getRiskColor(components.progress_anomaly_score || 0)}`
          }}
          onClick={() => onComponentClick?.('progress_risk')}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateX(4px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateX(0)';
          }}
          role="button"
          tabIndex={0}
          onKeyPress={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onComponentClick?.('progress_risk');
            }
          }}
          aria-label={`Progress risk score ${components.progress_anomaly_score?.toFixed(1) || 'N/A'}`}
        >
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            PROGRESS RISK
          </div>
          <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
            {components.progress_anomaly_score?.toFixed(1) || 'N/A'}
          </div>
        </div>

        <div
          style={{
            padding: spacing.md,
            backgroundColor: colors.background.tertiary,
            borderRadius: borderRadius.md,
            cursor: 'pointer',
            transition: 'all 150ms ease-in-out',
            borderLeft: `4px solid ${getRiskColor(components.governance_risk || 0)}`
          }}
          onClick={() => onComponentClick?.('governance_risk')}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateX(4px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateX(0)';
          }}
          role="button"
          tabIndex={0}
          onKeyPress={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onComponentClick?.('governance_risk');
            }
          }}
          aria-label={`Governance risk score ${components.governance_risk?.toFixed(1) || 'N/A'}`}
        >
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
            GOVERNANCE RISK
          </div>
          <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
            {components.governance_risk?.toFixed(1) || 'N/A'}
          </div>
        </div>
      </div>

      {/* Confidence */}
      {riskData.dcs?.dcs_score !== undefined && (
        <div style={{ marginTop: spacing.lg, paddingTop: spacing.lg, borderTop: `1px solid ${colors.border.default}` }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                DATA CONFIDENCE
              </div>
              <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
                {riskData.dcs.dcs_score?.toFixed(0) || 'N/A'}
              </div>
            </div>
            <Badge
              variant={riskData.dcs.dcs_score >= 80 ? 'success' : riskData.dcs.dcs_score >= 60 ? 'warning' : 'danger'}
              size="md"
            >
              {riskData.dcs.confidence_label || 'N/A'}
            </Badge>
          </div>
          
          {riskData.dcs.dcs_score < 60 && (
            <div style={{ 
              marginTop: spacing.sm, 
              padding: spacing.sm, 
              backgroundColor: `${colors.accent.warning}10`, 
              borderRadius: borderRadius.sm,
              fontSize: typography.fontSize.sm,
              color: colors.text.secondary,
              role: 'alert',
              'aria-live': 'polite'
            }}>
              ⚠️ This risk assessment may be affected by data-quality limitations.
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

export default memo(RiskDNA);
