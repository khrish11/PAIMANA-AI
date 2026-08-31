import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function InterventionBuilder({ scenarios, capabilities, onUpdate, disabled }) {
  const getParameterLabel = (param) => {
    switch (param) {
      case 'cost_overrun_ratio': return 'Cost Overrun Ratio';
      case 'schedule_slip_months': return 'Schedule Slip (Months)';
      case 'physical_progress': return 'Physical Progress (%)';
      default: return param;
    }
  };

  const getParameterRange = (param) => {
    if (capabilities?.supported_parameters?.[param]) {
      return capabilities.supported_parameters[param];
    }
    // Fallback defaults based on backend documentation
    switch (param) {
      case 'cost_overrun_ratio': return { min: 0.5, max: 3.0 };
      case 'schedule_slip_months': return { min: 0, max: 60 };
      case 'physical_progress': return { min: 0, max: 100 };
      default: return { min: 0, max: 100 };
    }
  };

  const getParameterUnit = (param) => {
    switch (param) {
      case 'cost_overrun_ratio': return '';
      case 'schedule_slip_months': return ' months';
      case 'physical_progress': return '%';
      default: return '';
    }
  };

  const handleSliderChange = (param, value) => {
    onUpdate(param, parseFloat(value));
  };

  const handleInputChange = (param, value) => {
    const numValue = parseFloat(value);
    if (!isNaN(numValue)) {
      onUpdate(param, numValue);
    }
  };

  const getDelta = (scenario) => {
    if (scenario.current_value === null || scenario.proposed_value === null) return null;
    const delta = scenario.proposed_value - scenario.current_value;
    return delta;
  };

  const getDeltaColor = (delta) => {
    if (delta === null) return colors.text.muted;
    if (delta < 0) return colors.accent.success;
    if (delta > 0) return colors.accent.danger;
    return colors.text.muted;
  };

  const getDeltaSign = (delta) => {
    if (delta === null) return '';
    if (delta > 0) return '+';
    return '';
  };

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          WHAT IF?
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Explore how changing project conditions could affect risk, cost, and schedule.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
        {scenarios.map((scenario) => {
          const range = getParameterRange(scenario.parameter);
          const delta = getDelta(scenario);
          
          return (
            <div key={scenario.parameter} style={{ 
              padding: spacing.lg,
              backgroundColor: colors.background.tertiary,
              borderRadius: '0.5rem',
              border: `1px solid ${colors.border.light}`
            }}>
              <div style={{ marginBottom: spacing.md }}>
                <h3 style={{ 
                  fontSize: typography.fontSize.lg, 
                  fontWeight: 600, 
                  color: colors.text.primary,
                  marginBottom: spacing.xs 
                }}>
                  {getParameterLabel(scenario.parameter)}
                </h3>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.lg, marginBottom: spacing.md }}>
                <div>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                    CURRENT
                  </div>
                  <div style={{ 
                    fontSize: typography.fontSize.xl, 
                    fontWeight: 600, 
                    color: colors.text.primary 
                  }}>
                    {scenario.current_value !== null && scenario.current_value !== undefined
                      ? `${scenario.current_value}${getParameterUnit(scenario.parameter)}`
                      : 'N/A'}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                    PROPOSED
                  </div>
                  <div style={{ 
                    fontSize: typography.fontSize.xl, 
                    fontWeight: 600, 
                    color: colors.accent.primary 
                  }}>
                    {scenario.proposed_value !== null && scenario.proposed_value !== undefined
                      ? `${scenario.proposed_value}${getParameterUnit(scenario.parameter)}`
                      : 'N/A'}
                  </div>
                </div>
              </div>

              {delta !== null && (
                <div style={{ marginBottom: spacing.md }}>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                    DELTA
                  </div>
                  <div style={{ 
                    fontSize: typography.fontSize.lg, 
                    fontWeight: 600, 
                    color: getDeltaColor(delta) 
                  }}>
                    {getDeltaSign(delta)}{delta.toFixed(2)}{getParameterUnit(scenario.parameter)}
                  </div>
                </div>
              )}

              <div style={{ marginBottom: spacing.md }}>
                <input
                  type="range"
                  min={range.min}
                  max={range.max}
                  step={scenario.parameter === 'physical_progress' ? 1 : 0.1}
                  value={scenario.proposed_value || range.min}
                  onChange={(e) => handleSliderChange(scenario.parameter, e.target.value)}
                  disabled={disabled}
                  style={{
                    width: '100%',
                    height: '8px',
                    borderRadius: '4px',
                    background: colors.border.default,
                    outline: 'none',
                    cursor: disabled ? 'not-allowed' : 'pointer',
                  }}
                />
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  fontSize: typography.fontSize.sm, 
                  color: colors.text.muted,
                  marginTop: spacing.xs 
                }}>
                  <span>{range.min}{getParameterUnit(scenario.parameter)}</span>
                  <span>{range.max}{getParameterUnit(scenario.parameter)}</span>
                </div>
              </div>

              <>
                <label htmlFor={`input-${scenario.parameter}`} style={{ 
                  fontSize: typography.fontSize.sm, 
                  color: colors.text.muted, 
                  marginBottom: spacing.xs,
                  display: 'block'
                }}>
                  Precise Value
                </label>
                <input
                  id={`input-${scenario.parameter}`}
                  type="number"
                  min={range.min}
                  max={range.max}
                  step={scenario.parameter === 'physical_progress' ? 1 : 0.1}
                  value={scenario.proposed_value || ''}
                  onChange={(e) => handleInputChange(scenario.parameter, e.target.value)}
                  disabled={disabled}
                  style={{
                    width: '100%',
                    padding: spacing.sm,
                    backgroundColor: colors.background.secondary,
                    border: `1px solid ${colors.border.default}`,
                    borderRadius: '0.375rem',
                    color: colors.text.primary,
                    fontSize: typography.fontSize.base,
                    cursor: disabled ? 'not-allowed' : 'text',
                  }}
                />
              </>
            </div>
          );
        })}
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
        <strong>Note:</strong> Adjust the parameters above to explore different scenarios. The simulation will calculate projected risk, cost, and schedule impacts based on your proposed values.
      </div>
    </Card>
  );
}
