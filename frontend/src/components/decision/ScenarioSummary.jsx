import { Card, Button } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function ScenarioSummary({ scenarios, onRun, disabled, simulationStatus }) {
  const getParameterLabel = (param) => {
    switch (param) {
      case 'cost_overrun_ratio': return 'Cost Overrun Ratio';
      case 'schedule_slip_months': return 'Schedule Slip';
      case 'physical_progress': return 'Physical Progress';
      default: return param;
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

  const hasChanges = scenarios.some(s => s.proposed_value !== s.current_value);

  const changedScenarios = scenarios.filter(s => s.proposed_value !== s.current_value);

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          SCENARIO {hasChanges ? 'READY' : 'SUMMARY'}
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          {hasChanges 
            ? 'Review your proposed changes before running the simulation.'
            : 'No changes configured. Adjust parameters in the What-If builder.'}
        </p>
      </div>

      {hasChanges && (
        <>
          <div style={{ 
            marginBottom: spacing.lg,
            padding: spacing.md,
            backgroundColor: `${colors.accent.warning}10`,
            borderRadius: '0.375rem',
            border: `1px solid ${colors.accent.warning}30`,
            fontSize: typography.fontSize.sm,
            color: colors.text.secondary
          }}>
            <strong>SIMULATION ONLY</strong>
            <br />
            Running this scenario does not modify the project. This is a counterfactual analysis for decision support.
          </div>

          <table style={{ 
            width: '100%',
            borderCollapse: 'collapse',
            marginBottom: spacing.lg
          }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${colors.border.light}` }}>
                <th style={{ 
                  textAlign: 'left', 
                  padding: spacing.md,
                  fontSize: typography.fontSize.sm,
                  color: colors.text.muted,
                  fontWeight: 600
                }}>
                  Parameter
                </th>
                <th style={{ 
                  textAlign: 'right', 
                  padding: spacing.md,
                  fontSize: typography.fontSize.sm,
                  color: colors.text.muted,
                  fontWeight: 600
                }}>
                  Current
                </th>
                <th style={{ 
                  textAlign: 'right', 
                  padding: spacing.md,
                  fontSize: typography.fontSize.sm,
                  color: colors.text.muted,
                  fontWeight: 600
                }}>
                  Proposed
                </th>
                <th style={{ 
                  textAlign: 'right', 
                  padding: spacing.md,
                  fontSize: typography.fontSize.sm,
                  color: colors.text.muted,
                  fontWeight: 600
                }}>
                  Change
                </th>
              </tr>
            </thead>
            <tbody>
              {changedScenarios.map((scenario) => {
                const delta = getDelta(scenario);
                return (
                  <tr key={scenario.parameter} style={{ borderBottom: `1px solid ${colors.border.light}` }}>
                    <td style={{ padding: spacing.md, color: colors.text.primary }}>
                      {getParameterLabel(scenario.parameter)}
                    </td>
                    <td style={{ 
                      padding: spacing.md, 
                      textAlign: 'right',
                      color: colors.text.secondary 
                    }}>
                      {scenario.current_value !== null && scenario.current_value !== undefined
                        ? `${scenario.current_value}${getParameterUnit(scenario.parameter)}`
                        : 'N/A'}
                    </td>
                    <td style={{ 
                      padding: spacing.md, 
                      textAlign: 'right',
                      color: colors.accent.primary,
                      fontWeight: 600
                    }}>
                      {scenario.proposed_value !== null && scenario.proposed_value !== undefined
                        ? `${scenario.proposed_value}${getParameterUnit(scenario.parameter)}`
                        : 'N/A'}
                    </td>
                    <td style={{ 
                      padding: spacing.md, 
                      textAlign: 'right',
                      color: getDeltaColor(delta),
                      fontWeight: 600
                    }}>
                      {delta !== null ? `${getDeltaSign(delta)}${delta.toFixed(2)}${getParameterUnit(scenario.parameter)}` : '-'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          <Button 
            variant="primary" 
            onClick={onRun}
            disabled={disabled || simulationStatus === 'SIMULATING'}
            style={{ width: '100%' }}
          >
            {simulationStatus === 'SIMULATING' ? 'SIMULATING...' : 'RUN COUNTERFACTUAL'}
          </Button>
        </>
      )}

      {!hasChanges && (
        <div style={{ 
          padding: spacing.xl,
          backgroundColor: colors.background.tertiary,
          borderRadius: '0.5rem',
          textAlign: 'center',
          color: colors.text.muted
        }}>
          Configure one or more parameters to enable simulation.
        </div>
      )}
    </Card>
  );
}
