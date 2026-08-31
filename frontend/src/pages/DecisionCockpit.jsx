import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Button, LoadingState, EmptyState } from '../components/common';
import { colors, spacing, typography } from '../tokens';
import { useCounterfactual } from '../hooks';
import {
  DecisionHeader,
  CurrentState,
  InterventionBuilder,
  ScenarioSummary,
  ScenarioComparison,
  ScenarioTransition,
  RiskImpact,
  CostImpact,
  ScheduleImpact,
  TradeoffAnalysis,
  ScenarioScorecard,
  SimulationEvidence,
  ScenarioAssumptions,
  ModelLimitations,
  DecisionContext
} from '../components/decision';

function DecisionCockpit() {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [projectLoading, setProjectLoading] = useState(true);
  const [projectError, setProjectError] = useState(null);

  const {
    capabilities,
    capabilitiesLoading,
    capabilitiesError,
    scenarios,
    updateScenario,
    result,
    isLoading,
    error,
    simulationStatus,
    baseline,
    hasChanges,
    runSimulation,
    resetSimulation,
    retry
  } = useCounterfactual(id);

  // Load project data
  useEffect(() => {
    async function fetchProject() {
      setProjectLoading(true);
      setProjectError(null);
      try {
        const response = await fetch(`/api/v1/projects/${id}`);
        if (!response.ok) throw new Error('Failed to fetch project');
        const data = await response.json();
        setProject(data);
      } catch (err) {
        setProjectError(err.message);
      } finally {
        setProjectLoading(false);
      }
    }
    fetchProject();
  }, [id]);

  const handleReset = () => {
    resetSimulation();
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  if (projectLoading || capabilitiesLoading) {
    return <LoadingState message="Loading decision cockpit..." />;
  }

  if (projectError || capabilitiesError) {
    return (
      <EmptyState 
        icon="⚠️" 
        title="Error" 
        description={projectError || capabilitiesError} 
      />
    );
  }

  // Check if simulation is unavailable
  if (capabilities && capabilities.available === false) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
        <Card padding="lg">
          <h2 style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary, marginBottom: spacing.md }}>
            DECISION COCKPIT
          </h2>
          <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary, marginBottom: spacing.lg }}>
            Explore interventions, compare projected outcomes, and support evidence-based decisions.
          </p>
          
          <div style={{ 
            padding: spacing.lg, 
            backgroundColor: `${colors.accent.warning}10`, 
            borderRadius: '0.5rem',
            border: `1px solid ${colors.accent.warning}30`,
            marginBottom: spacing.lg
          }}>
            <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
              COUNTERFACTUAL SIMULATION UNAVAILABLE
            </h3>
            <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary, marginBottom: spacing.md }}>
              {capabilities.message || "The Decision Cockpit simulator backend is not available."}
            </p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {/* Header */}
      <DecisionHeader 
        project={project}
        baseline={baseline}
        simulationStatus={simulationStatus}
        onReset={handleReset}
        onRefresh={handleRefresh}
      />

      {/* Error State */}
      {error && (
        <Card padding="lg" style={{ backgroundColor: `${colors.accent.danger}10`, border: `1px solid ${colors.accent.danger}30` }}>
          <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
            SIMULATION FAILED
          </h3>
          <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary, marginBottom: spacing.md }}>
            {error}
          </p>
          <div style={{ display: 'flex', gap: spacing.sm }}>
            <Button variant="primary" onClick={retry}>Retry</Button>
            <Button variant="secondary" onClick={handleReset}>Reset</Button>
          </div>
        </Card>
      )}

      {/* Current State */}
      <CurrentState baseline={baseline} />

      {/* What-If Builder and Scenario Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: spacing.lg }}>
        <InterventionBuilder 
          scenarios={scenarios}
          capabilities={capabilities}
          onUpdate={updateScenario}
          disabled={isLoading || simulationStatus === 'SIMULATING'}
        />
        <ScenarioSummary 
          scenarios={scenarios}
          onRun={runSimulation}
          disabled={!hasChanges || isLoading}
          simulationStatus={simulationStatus}
        />
      </div>

      {/* Simulation Results */}
      {result && result.available && result.results && (
        <>
          {/* Scenario Result Header */}
          <Card padding="lg" style={{ backgroundColor: `${colors.accent.success}10`, border: `2px solid ${colors.accent.success}30` }}>
            <h2 style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary, marginBottom: spacing.sm }}>
              SCENARIO RESULT
            </h2>
            <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
              Simulation completed successfully. Review the projected impacts below.
            </p>
          </Card>

          {/* Scenario Comparison */}
          <ScenarioComparison result={result} />

          {/* Scenario Transition */}
          <ScenarioTransition result={result} />

          {/* Impact Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: spacing.lg }}>
            <RiskImpact result={result} />
            <CostImpact result={result} />
            <ScheduleImpact result={result} />
          </div>

          {/* Trade-Off Analysis */}
          <TradeoffAnalysis result={result} />

          {/* Scenario Scorecard */}
          <ScenarioScorecard result={result} />

          {/* Evidence and Assumptions */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: spacing.lg }}>
            <SimulationEvidence result={result} scenarios={scenarios} />
            <ScenarioAssumptions />
          </div>

          {/* Model Limitations */}
          <ModelLimitations />

          {/* Decision Context */}
          <DecisionContext baseline={baseline} result={result} />
        </>
      )}

      {/* Empty State - No Simulation Run */}
      {!result && !isLoading && (
        <Card padding="lg">
          <div style={{ 
            padding: spacing.xl,
            backgroundColor: colors.background.tertiary,
            borderRadius: '0.5rem',
            textAlign: 'center',
            color: colors.text.muted
          }}>
            Configure one or more project parameters and run a counterfactual simulation to see projected impacts.
          </div>
        </Card>
      )}
    </div>
  );
}

export default DecisionCockpit;
