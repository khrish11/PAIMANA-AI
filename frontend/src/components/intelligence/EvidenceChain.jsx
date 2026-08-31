import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function EvidenceChain({ intelligence }) {
  const { data } = intelligence;

  const risk = data.risk;
  const pbe = data.pbe;
  const rcf = data.rcf;

  // Build evidence chain from available data
  const chainSteps = [];

  // Step 1: Project Data
  if (risk) {
    chainSteps.push({
      step: 'PROJECT DATA',
      value: `Physical progress: ${risk.project_name ? 'Available' : 'N/A'}`,
      source: 'Project Records',
      type: 'data'
    });
  }

  // Step 2: Model Signal (Risk)
  if (risk && risk.composite_score !== null) {
    chainSteps.push({
      step: 'RISK MODEL',
      value: `Risk score: ${risk.composite_score.toFixed(1)}`,
      source: 'Risk Model',
      type: 'model'
    });
  }

  // Step 3: Intelligence Finding (Peer)
  if (pbe && pbe.percentile !== null) {
    chainSteps.push({
      step: 'PEER BENCHMARK',
      value: pbe.percentile > 50 ? 'Below comparable projects' : 'Above comparable projects',
      source: 'Peer Benchmark Engine',
      type: 'intelligence'
    });
  }

  // Step 4: Intelligence Finding (Forecast)
  if (rcf && rcf.p80_completion_months !== null) {
    chainSteps.push({
      step: 'FORECAST',
      value: rcf.p80_completion_months > 36 ? 'Completion pressure detected' : 'On track',
      source: 'Reference Class Forecast',
      type: 'intelligence'
    });
  }

  // Step 5: Decision Context
  if (risk && risk.composite_score !== null) {
    const category = risk.composite_score >= 60 ? 'requires closer monitoring' : 'within normal parameters';
    chainSteps.push({
      step: 'DECISION CONTEXT',
      value: `Project ${category}`,
      source: 'Derived from intelligence',
      type: 'decision'
    });
  }

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          EVIDENCE CHAIN
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Visual chain from project data to decision implications.
        </p>
      </div>

      {chainSteps.length === 0 ? (
        <div style={{ 
          padding: spacing.xl,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          textAlign: 'center',
          color: colors.text.muted
        }}>
          Insufficient data to build evidence chain.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
          {chainSteps.map((step, index) => (
            <div key={index} style={{ display: 'flex', alignItems: 'center', gap: spacing.md }}>
              {/* Step Box */}
              <div style={{ 
                flex: 1,
                padding: spacing.lg,
                backgroundColor: colors.background.tertiary,
                borderRadius: '0.5rem',
                border: `1px solid ${colors.border.light}`,
                borderLeft: `4px solid ${
                  step.type === 'data' ? colors.accent.primary :
                  step.type === 'model' ? colors.accent.warning :
                  step.type === 'intelligence' ? colors.accent.info :
                  colors.accent.success
                }`
              }}>
                <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                  {step.step}
                </div>
                <div style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
                  {step.value}
                </div>
                <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, marginTop: spacing.xs }}>
                  Source: {step.source}
                </div>
              </div>

              {/* Arrow (not for last step) */}
              {index < chainSteps.length - 1 && (
                <div style={{ 
                  fontSize: typography.fontSize['2xl'],
                  color: colors.accent.primary,
                  fontWeight: 700,
                  minWidth: '40px',
                  textAlign: 'center'
                }}>
                  ↓
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Legend */}
      <div style={{ marginTop: spacing.lg, display: 'flex', gap: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: colors.accent.primary, borderRadius: '2px' }}></div>
          <span>Project Data</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: colors.accent.warning, borderRadius: '2px' }}></div>
          <span>Model Signal</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: colors.accent.info, borderRadius: '2px' }}></div>
          <span>Intelligence Finding</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: colors.accent.success, borderRadius: '2px' }}></div>
          <span>Decision Context</span>
        </div>
      </div>

      <div style={{ marginTop: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>IMPORTANT:</strong> Each connection is based on available backend data. Causal relationships are not claimed unless explicitly supported by the model.
      </div>
    </Card>
  );
}
