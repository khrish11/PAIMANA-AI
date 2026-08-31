export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

// Projects
export async function getProjects(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.append(key, value);
  });
  const response = await fetch(`${apiBaseUrl}/projects?${params}`);
  if (!response.ok) throw new Error('Failed to fetch projects');
  return response.json();
}

export async function getProjectRisk(projectId) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/risk`);
  if (!response.ok) throw new Error('Failed to fetch project risk');
  return response.json();
}

export async function getProjectHistory(projectId) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/history`);
  if (!response.ok) throw new Error('Failed to fetch project history');
  return response.json();
}

export async function createProject(projectData) {
  const response = await fetch(`${apiBaseUrl}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(projectData),
  });
  if (!response.ok) throw new Error('Failed to create project');
  return response.json();
}

export async function updateProject(projectId, projectData) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(projectData),
  });
  if (!response.ok) throw new Error('Failed to update project');
  return response.json();
}

// Submissions
export async function createSubmission(submissionData) {
  const response = await fetch(`${apiBaseUrl}/submissions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(submissionData),
  });
  if (!response.ok) throw new Error('Failed to create submission');
  return response.json();
}

// Imports
export async function previewImport(file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${apiBaseUrl}/imports/preview`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Failed to preview import');
  return response.json();
}

export async function createImport(file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${apiBaseUrl}/imports`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Failed to create import');
  return response.json();
}

export async function getImport(importId) {
  const response = await fetch(`${apiBaseUrl}/imports/${importId}`);
  if (!response.ok) throw new Error('Failed to fetch import');
  return response.json();
}

// Data Health
export async function getDataHealth() {
  const response = await fetch(`${apiBaseUrl}/data-health`);
  if (!response.ok) throw new Error('Failed to fetch data health');
  return response.json();
}

// Audit
export async function getAuditTrail(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.append(key, value);
  });
  const response = await fetch(`${apiBaseUrl}/audit?${params}`);
  if (!response.ok) throw new Error('Failed to fetch audit trail');
  return response.json();
}

// Reports
export async function getNationalReport(reportingPeriod = '2026-03') {
  const response = await fetch(`${apiBaseUrl}/reports/national?reporting_period=${reportingPeriod}`);
  if (!response.ok) throw new Error('Failed to fetch national report');
  return response.json();
}

export async function getProjectReport(projectId, reportingPeriod = '2026-03') {
  const response = await fetch(`${apiBaseUrl}/reports/project/${projectId}?reporting_period=${reportingPeriod}`);
  if (!response.ok) throw new Error('Failed to fetch project report');
  return response.json();
}

export async function getSectorReport(sector, reportingPeriod = '2026-03') {
  const response = await fetch(`${apiBaseUrl}/reports/sector/${sector}?reporting_period=${reportingPeriod}`);
  if (!response.ok) throw new Error('Failed to fetch sector report');
  return response.json();
}

export async function getStateReport(state, reportingPeriod = '2026-03') {
  const response = await fetch(`${apiBaseUrl}/reports/state/${state}?reporting_period=${reportingPeriod}`);
  if (!response.ok) throw new Error('Failed to fetch state report');
  return response.json();
}

export async function getGovernanceReport(reportingPeriod = '2026-03') {
  const response = await fetch(`${apiBaseUrl}/reports/governance?reporting_period=${reportingPeriod}`);
  if (!response.ok) throw new Error('Failed to fetch governance report');
  return response.json();
}

export async function getModelReport(reportingPeriod = '2026-03') {
  const response = await fetch(`${apiBaseUrl}/reports/models?reporting_period=${reportingPeriod}`);
  if (!response.ok) throw new Error('Failed to fetch model report');
  return response.json();
}

export async function getReportHistory(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.append(key, value);
  });
  const response = await fetch(`${apiBaseUrl}/reports/history?${params}`);
  if (!response.ok) throw new Error('Failed to fetch report history');
  return response.json();
}

// Dashboard
export async function getDashboard() {
  const response = await fetch(`${apiBaseUrl}/dashboard`);
  if (!response.ok) throw new Error('Failed to fetch dashboard');
  return response.json();
}

// Model Performance
export async function getModelPerformance() {
  const response = await fetch(`${apiBaseUrl}/admin/models`);
  if (!response.ok) throw new Error('Failed to fetch model performance');
  return response.json();
}

// RCF (Reference Class Forecast)
export async function getProjectRCF(projectId) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/rcf`);
  if (!response.ok) throw new Error('Failed to fetch project RCF');
  return response.json();
}

// Counterfactual Simulation
export async function getSimulationCapabilities(projectId) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/simulate`);
  if (!response.ok) throw new Error('Failed to fetch simulation capabilities');
  return response.json();
}

export async function runSimulation(projectId, scenarios) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_id: projectId,
      scenarios: scenarios
    }),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Simulation failed' }));
    throw new Error(error.detail || 'Failed to run simulation');
  }
  
  return response.json();
}

// NID (Narrative Intelligence Detection)
export async function getProjectNID(projectId) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/nid`);
  if (!response.ok) throw new Error('Failed to fetch NID data');
  return response.json();
}

// PBE (Peer Benchmark Engine)
export async function getProjectPBE(projectId) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/pbe`);
  if (!response.ok) throw new Error('Failed to fetch PBE data');
  return response.json();
}

// Risk Trend
export async function getProjectTrend(projectId) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/trend`);
  if (!response.ok) throw new Error('Failed to fetch risk trend');
  return response.json();
}

// Network Intelligence
export async function getProjectNetwork(projectId) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/network`);
  if (!response.ok) throw new Error('Failed to fetch network data');
  return response.json();
}

// Global Network
export async function getNetwork() {
  const response = await fetch(`${apiBaseUrl}/network`);
  if (!response.ok) throw new Error('Failed to fetch global network');
  return response.json();
}

// Blast Radius Analysis
export async function getBlastRadius(projectId, depth = 2, relationshipTypes = null, riskThreshold = 'HIGH') {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/network/blast-radius`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      depth,
      relationship_types: relationshipTypes,
      risk_threshold: riskThreshold
    })
  });
  if (!response.ok) throw new Error('Failed to fetch blast radius');
  return response.json();
}

// Positive Deviance Radar (PDR)
export async function getPositiveDeviants(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.append(key, value);
  });
  const response = await fetch(`${apiBaseUrl}/positive-deviants?${params}`);
  if (!response.ok) throw new Error('Failed to fetch positive deviants');
  return response.json();
}

export async function getPlaybooks(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.append(key, value);
  });
  const response = await fetch(`${apiBaseUrl}/playbooks?${params}`);
  if (!response.ok) throw new Error('Failed to fetch playbooks');
  return response.json();
}

export async function getPlaybookDetail(playbookId) {
  const response = await fetch(`${apiBaseUrl}/playbooks/${playbookId}`);
  if (!response.ok) throw new Error('Failed to fetch playbook detail');
  return response.json();
}

export async function getSuggestedPlaybooks(projectId) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/suggested-playbooks`);
  if (!response.ok) throw new Error('Failed to fetch suggested playbooks');
  return response.json();
}

export async function dismissPlaybookSuggestion(projectId, suggestionId) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/suggested-playbooks/${suggestionId}/dismiss`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error('Failed to dismiss playbook suggestion');
  return response.json();
}

export async function markPlaybookSuggestionViewed(projectId, suggestionId) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/suggested-playbooks/${suggestionId}/viewed`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) throw new Error('Failed to mark playbook suggestion as viewed');
  return response.json();
}

// Governance
export async function getGovernanceQueue() {
  const response = await fetch(`${apiBaseUrl}/governance/queue`);
  if (!response.ok) throw new Error('Failed to fetch governance queue');
  return response.json();
}

export async function submitGovernanceAction(actionData) {
  const response = await fetch(`${apiBaseUrl}/governance/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(actionData),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Governance action failed' }));
    throw new Error(error.detail || 'Failed to submit governance action');
  }
  return response.json();
}

export async function getProjectGovernanceActions(projectId) {
  const response = await fetch(`${apiBaseUrl}/governance/projects/${projectId}/actions`);
  if (!response.ok) throw new Error('Failed to fetch project governance actions');
  return response.json();
}

// Single project detail
export async function getProject(projectId) {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}`);
  if (!response.ok) throw new Error('Failed to fetch project');
  return response.json();
}
