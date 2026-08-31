import { useState, useEffect, useCallback } from 'react';
import { getSimulationCapabilities, runSimulation, getProjectRisk } from '../services/api';

export function useCounterfactual(projectId) {
  const [capabilities, setCapabilities] = useState(null);
  const [capabilitiesLoading, setCapabilitiesLoading] = useState(true);
  const [capabilitiesError, setCapabilitiesError] = useState(null);

  const [scenarios, setScenarios] = useState([]);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [simulationStatus, setSimulationStatus] = useState('READY'); // READY, SIMULATING, COMPLETE, FAILED

  const [baseline, setBaseline] = useState(null);

  // Load capabilities on mount
  useEffect(() => {
    async function loadCapabilities() {
      setCapabilitiesLoading(true);
      setCapabilitiesError(null);
      try {
        const data = await getSimulationCapabilities(projectId);
        setCapabilities(data);
        
        // Initialize scenarios with current values from capabilities
        if (data.available && data.supported_parameters) {
          const initialScenarios = Object.keys(data.supported_parameters).map(param => ({
            parameter: param,
            current_value: null, // Will be populated from project data
            proposed_value: null,
          }));
          setScenarios(initialScenarios);
        }
      } catch (err) {
        setCapabilitiesError(err.message);
      } finally {
        setCapabilitiesLoading(false);
      }
    }
    
    if (projectId) {
      loadCapabilities();
    }
  }, [projectId]);

  // Load baseline project data
  useEffect(() => {
    async function loadBaseline() {
      try {
        const riskData = await getProjectRisk(projectId);
        setBaseline(riskData);
        
        // Update scenario current values from baseline
        if (riskData && scenarios.length > 0) {
          setScenarios(prev => prev.map(scenario => {
            let currentValue = null;
            
            // Map backend fields to scenario parameters
            if (scenario.parameter === 'cost_overrun_ratio') {
              currentValue = riskData.cost_overrun_ratio || 1.0;
            } else if (scenario.parameter === 'schedule_slip_months') {
              currentValue = riskData.schedule_slip_months || 0;
            } else if (scenario.parameter === 'physical_progress') {
              currentValue = riskData.physical_progress || 0;
            }
            
            return {
              ...scenario,
              current_value: currentValue,
              proposed_value: currentValue, // Initialize proposed to current
            };
          }));
        }
      } catch (err) {
        console.error('Failed to load baseline:', err);
      }
    }
    
    if (projectId && scenarios.length > 0) {
      loadBaseline();
    }
  }, [projectId, scenarios.length]);

  const updateScenario = useCallback((parameter, proposedValue) => {
    setScenarios(prev => prev.map(scenario => 
      scenario.parameter === parameter
        ? { ...scenario, proposed_value: proposedValue }
        : scenario
    ));
  }, []);

  const runSimulationRequest = useCallback(async () => {
    if (!capabilities || !capabilities.available) {
      setError('Simulation capabilities not available');
      return;
    }

    // Validate scenarios
    const validScenarios = scenarios.filter(s => 
      s.proposed_value !== null && 
      s.proposed_value !== s.current_value
    );

    if (validScenarios.length === 0) {
      setError('No scenario changes to simulate');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSimulationStatus('SIMULATING');

    try {
      const response = await runSimulation(projectId, validScenarios);
      setResult(response);
      setSimulationStatus('COMPLETE');
    } catch (err) {
      setError(err.message);
      setSimulationStatus('FAILED');
    } finally {
      setIsLoading(false);
    }
  }, [projectId, scenarios, capabilities]);

  const resetSimulation = useCallback(() => {
    setResult(null);
    setError(null);
    setSimulationStatus('READY');
    
    // Reset proposed values to current values
    setScenarios(prev => prev.map(scenario => ({
      ...scenario,
      proposed_value: scenario.current_value,
    })));
  }, []);

  const retry = useCallback(() => {
    setError(null);
    setSimulationStatus('READY');
  }, []);

  const hasChanges = scenarios.some(s => s.proposed_value !== s.current_value);

  return {
    capabilities,
    capabilitiesLoading,
    capabilitiesError,
    scenarios,
    setScenarios,
    updateScenario,
    result,
    isLoading,
    error,
    simulationStatus,
    baseline,
    hasChanges,
    runSimulation: runSimulationRequest,
    resetSimulation,
    retry,
  };
}
