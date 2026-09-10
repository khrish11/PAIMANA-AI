import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function ModelLimitations() {
  const limitations = [
    {
      category: 'CONFIDENCE',
      status: 'NOT AVAILABLE',
      description: 'Current PAIMANA risk model does not provide a confidence score for simulation results.'
    },
    {
      category: 'UNCERTAINTY',
      status: 'NOT AVAILABLE',
      description: 'Current simulation engine does not provide prediction intervals or uncertainty quantification.'
    },
    {
      category: 'SCHEDULE ESTIMATION',
      status: 'SIMPLIFIED',
      description: 'Schedule estimation uses a simplified formula (36 months + schedule slip) rather than full RCF forecast integration.'
    },
    {
      category: 'RCF SCENARIO INTEGRATION',
      status: 'NOT IMPLEMENTED',
      description: 'Reference Class Forecasting counterfactual scenarios are not yet integrated.'
    },
    {
      category: 'PBE COUNTERFACTUAL',
      status: 'NOT AVAILABLE',
      description: 'Peer Benchmark Engine does not accept scenario inputs for counterfactual percentile calculation.'
    },
    {
      category: 'NID COUNTERFACTUAL',
      status: 'NOT AVAILABLE',
      description: 'Narrative Intelligence Detection does not recalculate for scenario states.'
    },
    {
      category: 'SCENARIO PERSISTENCE',
      status: 'NOT IMPLEMENTED',
      description: 'Scenarios are not persisted; each simulation is independent.'
    },
    {
      category: 'AUDIT INTEGRATION',
      status: 'NOT AVAILABLE',
      description: 'Simulation audit records are not currently available.'
    },
    {
      category: 'CALIBRATION',
      status: 'NOT IMPLEMENTED',
      description: 'ML v2 models are uncalibrated. Probabilities may not be well-calibrated. Use ranking (ROC-AUC) not absolute probabilities.'
    },
    {
      category: 'TEMPORAL VALIDATION',
      status: 'PARTIAL',
      description: 'Schedule v2 model uses stratified split (not temporal) to fix label shift. May have some temporal leakage.'
    },
    {
      category: 'GEOGRAPHIC BIAS',
      status: 'MODERATE',
      description: 'Schedule v2 model dominated by state features. May not generalize well to new states.'
    }
  ];

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          MODEL LIMITATIONS
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Current capabilities and known limitations of the simulation engine.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        {limitations.map((limitation, index) => (
          <div key={index} style={{ 
            padding: spacing.md,
            backgroundColor: colors.background.tertiary,
            borderRadius: '0.375rem',
            border: `1px solid ${colors.border.light}`
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: spacing.xs }}>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, fontWeight: 600 }}>
                {limitation.category}
              </div>
              <div style={{ 
                fontSize: typography.fontSize.sm, 
                color: limitation.status === 'NOT AVAILABLE' || limitation.status === 'NOT IMPLEMENTED' 
                  ? colors.accent.warning 
                  : colors.accent.info,
                fontWeight: 600
              }}>
                {limitation.status}
              </div>
            </div>
            <div style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
              {limitation.description}
            </div>
          </div>
        ))}
      </div>

      <div style={{ 
        marginTop: spacing.lg,
        padding: spacing.md,
        backgroundColor: `${colors.accent.warning}10`,
        borderRadius: '0.375rem',
        border: `1px solid ${colors.accent.warning}30`,
        fontSize: typography.fontSize.sm,
        color: colors.text.secondary
      }}>
        <strong>Transparency:</strong> These limitations are documented to ensure appropriate interpretation of simulation results. The simulation provides value within these constraints.
      </div>
    </Card>
  );
}
