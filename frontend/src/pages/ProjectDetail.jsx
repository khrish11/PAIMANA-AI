import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getProjectRCF } from '../services/api';
import { Card, Badge, Button, LoadingState, EmptyState } from '../components/common';
import { SHAPWaterfall } from '../components/charts';
import { DCSCard, AnomalyCard } from '../components/domain';
import { 
  RiskDNA, 
  RiskBreakdown, 
  RiskJourney, 
  ReferenceClassCard, 
  ForecastIntelligence, 
  ProjectTimeline, 
  EvidenceDrawer, 
  IntelligenceHeader, 
  EvidenceMetadata 
} from '../components/intelligence';
import { NIDSummary } from '../components/nid';
import { PeerBenchmarkSummary } from '../components/pbe';
import { PlaybookCard } from '../components/playbooks';
import { useProjectRisk, useRiskHistory, useNID, usePBE, usePositiveDeviance } from '../hooks';
import { colors, spacing, typography, borderRadius } from '../tokens';

function ProjectDetail() {
  const { id } = useParams();
  const [evidenceDrawerOpen, setEvidenceDrawerOpen] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const [rcfData, setRcfData] = useState(null);
  const [rcfLoading, setRcfLoading] = useState(true);
  const [rcfError, setRcfError] = useState(null);

  const { data: riskData, loading: riskLoading, error: riskError, retry: retryRisk } = useProjectRisk(id);
  const { data: historyData, loading: historyLoading } = useRiskHistory(id);
  const { data: nidData, loading: nidLoading } = useNID(id);
  const { data: pbeData, loading: pbeLoading } = usePBE(id);
  const { suggestions, loading: suggestionsLoading, error: suggestionsError, dismissSuggestion, markSuggestionViewed } = usePositiveDeviance(id);

  useEffect(() => {
    async function fetchRCF() {
      try {
        setRcfLoading(true);
        const response = await getProjectRCF(id);
        setRcfData(response);
      } catch (err) {
        setRcfError(err.message);
      } finally {
        setRcfLoading(false);
      }
    }
    if (id) fetchRCF();
  }, [id]);

  const handleWhyClick = () => {
    if (riskData) {
      setSelectedEvidence({
        risk_score: riskData.composite_score,
        risk_category: riskData.risk_category,
        confidence: riskData.dcs?.dcs_score,
        shap_drivers: riskData.shap?.drivers,
        explanation: riskData.calibration?.weights ? 'Risk computed using calibrated model weights' : 'Risk explanation unavailable',
        supporting_data: {
          'Cost Risk': riskData.components?.cost_risk,
          'Schedule Risk': riskData.components?.schedule_risk,
          'Progress Risk': riskData.components?.progress_anomaly_score,
          'Governance Risk': riskData.components?.governance_risk,
        },
        timestamp: riskData.reporting_month,
        model_version: riskData.ml_model_version,
        source: 'Project CUF',
      });
      setEvidenceDrawerOpen(true);
    }
  };

  const handleComponentClick = (component) => {
    if (riskData) {
      setSelectedEvidence({
        risk_score: riskData.components?.[component],
        risk_category: riskData.risk_category,
        confidence: riskData.dcs?.dcs_score,
        shap_drivers: riskData.shap?.drivers?.slice(0, 3),
        explanation: `Component risk breakdown for ${component.replace('_', ' ')}`,
        supporting_data: {
          'Component': component,
          'Value': riskData.components?.[component],
        },
        timestamp: riskData.reporting_month,
        model_version: riskData.ml_model_version,
        source: 'Project CUF',
      });
      setEvidenceDrawerOpen(true);
    }
  };

  if (riskLoading) return <LoadingState message="Loading project details..." />;
  if (riskError) return (
    <EmptyState 
      icon="⚠️" 
      title="Risk Intelligence Unavailable" 
      description="We couldn't retrieve the project risk intelligence."
    >
      <Button variant="primary" onClick={retryRisk}>Retry</Button>
    </EmptyState>
  );

  const projectMilestones = [
    { name: 'DPR', description: 'Detailed Project Report', status: 'completed', date: riskData?.approval_date || 'N/A' },
    { name: 'Financial Closure', description: 'Financial approval completed', status: 'completed', date: 'N/A' },
    { name: 'Execution', description: 'Project execution phase', status: 'in_progress', date: 'N/A', delay: riskData?.components?.schedule_risk > 50 ? Math.floor(riskData.components.schedule_risk / 10) : 0, governance_status: 'Active' },
    { name: '50% Progress', description: 'Halfway completion milestone', status: 'pending', date: 'N/A' },
    { name: 'Completion', description: 'Project completion', status: 'pending', date: riskData?.planned_completion_date || 'N/A' },
  ];

  const forecastData = rcfData ? {
    cost_forecast: {
      current_baseline: riskData?.sanctioned_cost || 0,
      p50: rcfData.p50_final_cost,
      p80: rcfData.p80_final_cost,
      p90: rcfData.p90_final_cost,
      variance: rcfData.cost_overrun_p50 * 100,
    },
    completion_forecast: {
      planned_date: riskData?.planned_completion_date || 'N/A',
      p50: `${rcfData.p50_completion_months} months`,
      p80: `${rcfData.p80_completion_months} months`,
      p90: `${rcfData.p90_completion_months} months`,
      delay_months: rcfData.schedule_delay_p50,
    },
    reference_class_comparison: rcfData.reference_class,
  } : null;

  const referenceData = rcfData ? {
    sector: rcfData.sector,
    size_band: rcfData.size_band,
    region: rcfData.region,
    comparable_count: rcfData.sample_count,
    current_percentile: Math.floor((rcfData.cost_overrun_p50 / 0.5) * 100),
    cohort_median: 50,
    p75: 75,
    p90: 90,
  } : null;

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      gap: spacing.xl,
      maxWidth: '100%',
      overflow: 'hidden'
    }}>
      {/* Project Metadata & Provenance */}
      <Card padding="lg">
        <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
          Project Information
        </h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: spacing.lg }}>
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Project Code
            </div>
            <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
              {riskData?.project_code || 'N/A'}
            </div>
          </div>
          
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Project ID
            </div>
            <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
              {riskData?.project_id || 'N/A'}
            </div>
          </div>
          
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Ministry
            </div>
            <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
              {riskData?.ministry || 'N/A'}
            </div>
          </div>
          
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Sector
            </div>
            <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
              {riskData?.sector || 'N/A'}
            </div>
          </div>
          
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              State
            </div>
            <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
              {riskData?.state || 'N/A'}
            </div>
          </div>
          
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Implementing Agency
            </div>
            <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
              {riskData?.implementing_agency || 'N/A'}
            </div>
          </div>
          
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Sanctioned Cost
            </div>
            <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
              {riskData?.sanctioned_cost ? `₹${riskData.sanctioned_cost.toFixed(2)} Cr` : 'N/A'}
            </div>
          </div>
          
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Approval Date
            </div>
            <div style={{ fontSize: typography.fontSize.base, color: colors.text.primary }}>
              {riskData?.approval_date ? new Date(riskData.approval_date).toLocaleDateString() : 'N/A'}
            </div>
          </div>
        </div>

        {/* Provenance Section */}
        <div style={{ 
          marginTop: spacing.lg, 
          paddingTop: spacing.lg,
          borderTop: `1px solid ${colors.border.default}`
        }}>
          <h4 style={{ 
            fontSize: typography.fontSize.base, 
            fontWeight: 600, 
            color: colors.text.primary,
            marginBottom: spacing.md 
          }}>
            Data Provenance
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: spacing.md }}>
            <div>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                Data Source
              </div>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                {riskData?.data_source || 'CUF Submission'}
              </div>
            </div>
            
            <div>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                Latest Reporting Month
              </div>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                {riskData?.reporting_month ? new Date(riskData.reporting_month).toLocaleDateString() : 'N/A'}
              </div>
            </div>
            
            <div>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                Last Updated
              </div>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                {riskData?.last_updated ? new Date(riskData.last_updated).toLocaleString() : 'N/A'}
              </div>
            </div>
            
            <div>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                Import Method
              </div>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                {riskData?.import_method || 'Manual Entry'}
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Intelligence Header */}
      <IntelligenceHeader
        title={riskData?.project_name || 'Project'}
        subtitle={`Project ID: ${riskData?.project_id || 'N/A'} • ${riskData?.sector || 'N/A'} • ${riskData?.state || 'N/A'}`}
        status={riskData?.risk_category}
        timestamp={riskData?.reporting_month}
        confidence={riskData?.dcs?.dcs_score}
        onWhyClick={handleWhyClick}
        actions={[
          { label: 'Edit Project', variant: 'primary', size: 'sm' },
          { label: 'Add Monthly Update', variant: 'secondary', size: 'sm', onClick: () => window.location.href = '/data-entry' },
          { label: 'Version History', variant: 'ghost', size: 'sm', onClick: () => window.location.href = `/projects/${id}/history` },
          { label: 'Generate Report', variant: 'secondary', size: 'sm', onClick: () => window.location.href = `/reports/project/${id}` },
          { label: 'Decision Cockpit', variant: 'ghost', size: 'sm', onClick: () => window.location.href = `/projects/${id}/decision-cockpit` },
          { label: 'Network Risk', variant: 'ghost', size: 'sm', onClick: () => window.location.href = '/network' },
        ]}
      />

      {/* Experimental ML Warning Banner */}
      {riskData?.ml_model_status === 'experimental' && (
        <div style={{
          padding: spacing.md,
          backgroundColor: `${colors.accent.warning}10`,
          borderLeft: `4px solid ${colors.accent.warning}`,
          borderRadius: borderRadius.sm,
        }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: spacing.sm }}>
            <span style={{ fontSize: '1.25rem' }}>⚠️</span>
            <div>
              <div style={{ 
                fontWeight: 600,
                color: colors.accent.warning,
                marginBottom: spacing.xs 
              }}>
                EXPERIMENTAL MODEL
              </div>
              <div style={{ 
                fontSize: typography.fontSize.sm,
                color: colors.text.secondary 
              }}>
                Limited completed outcomes. Not production validated.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Project Risk DNA */}
      <RiskDNA 
        riskData={riskData} 
        onWhyClick={handleWhyClick} 
        onComponentClick={handleComponentClick} 
      />

      {/* ML Predictions */}
      {riskData?.ml_model_status === 'success' && (
        <Card padding="lg">
          <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
            ML-Driven Risk Predictions
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: spacing.lg }}>
            {/* Cost Overrun Prediction */}
            <div style={{
              padding: spacing.md,
              backgroundColor: colors.background.tertiary,
              borderRadius: borderRadius.md,
              border: `1px solid ${colors.border.default}`
            }}>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                Cost Overrun Risk
              </div>
              <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 600, color: colors.text.primary, marginBottom: spacing.xs }}>
                {riskData.shap?.predicted_probability ? `${(riskData.shap.predicted_probability * 100).toFixed(1)}%` : 'N/A'}
              </div>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, marginBottom: spacing.sm }}>
                Probability of >10% cost overrun
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                <Badge variant={riskData.shap?.predicted_probability > 0.5 ? 'danger' : 'success'} size="sm">
                  {riskData.shap?.predicted_probability > 0.5 ? 'HIGH RISK' : 'LOW RISK'}
                </Badge>
                <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>
                  Model: {riskData.ml_model_version || 'v2'}
                </div>
              </div>
            </div>

            {/* Schedule Delay Prediction */}
            <div style={{
              padding: spacing.md,
              backgroundColor: colors.background.tertiary,
              borderRadius: borderRadius.md,
              border: `1px solid ${colors.border.default}`
            }}>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                Schedule Delay Risk
              </div>
              <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 600, color: colors.text.primary, marginBottom: spacing.xs }}>
                {riskData.ml_schedule_probability ? `${(riskData.ml_schedule_probability * 100).toFixed(1)}%` : 'N/A'}
              </div>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, marginBottom: spacing.sm }}>
                Probability of >6 month delay
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                <Badge variant={riskData.ml_schedule_probability > 0.5 ? 'danger' : 'warning'} size="sm">
                  {riskData.ml_schedule_probability > 0.5 ? 'HIGH RISK' : 'MODERATE RISK'}
                </Badge>
                <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>
                  Model: {riskData.ml_model_version || 'v2'}
                </div>
              </div>
            </div>
          </div>

          <div style={{
            marginTop: spacing.md,
            padding: spacing.md,
            backgroundColor: `${colors.accent.info}10`,
            borderRadius: borderRadius.sm,
            borderLeft: `3px solid ${colors.accent.info}`
          }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              <strong>ML Model Status:</strong> {riskData.ml_model_status} • 
              <strong> Version:</strong> {riskData.ml_model_version || '2.0'} • 
              <strong> Method:</strong> {riskData.shap?.method || 'XGBoost + LightGBM'}
            </div>
          </div>
        </Card>
      )}

      {/* Model Transparency */}
      {riskData?.ml_model_status && (
        <Card padding="lg">
          <h3 style={{ marginBottom: spacing.md }}>Model Transparency</h3>
          <EvidenceMetadata
            model={riskData.ml_model_version || 'XGBoost'}
            predictionTimestamp={riskData.reporting_month}
            lastDataUpdate={riskData.reporting_month}
            confidence={riskData.dcs?.dcs_score}
            source="Project CUF"
          />
        </Card>
      )}

      {/* Risk Breakdown with SHAP */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: spacing.lg,
        '@media (max-width: 768px)': {
          gridTemplateColumns: '1fr',
        }
      }}>
        <RiskBreakdown 
          riskData={{
            composite_score: riskData?.composite_score,
            component_scores: riskData?.components,
            risk_category: riskData?.risk_category,
          }} 
          onWhyClick={handleWhyClick} 
        />
        
        {riskData?.shap?.drivers && riskData.shap.drivers.length > 0 && (
          <Card padding="lg">
            <h3 style={{ marginBottom: spacing.md }}>Top Risk Drivers (SHAP)</h3>
            <SHAPWaterfall
              values={riskData.shap.drivers.slice(0, 5).map(d => ({
                feature: d.human_label,
                value: d.feature_value,
                contribution: d.contribution,
                direction: d.direction === 'increases_risk' ? 'positive' : 'negative',
                explanation: d.explanation,
              }))}
              baseValue={0}
              finalValue={riskData.composite_score}
            />
          </Card>
        )}
      </div>

      {/* Forecast Intelligence */}
      {rcfLoading ? (
        <LoadingState message="Loading forecast intelligence..." />
      ) : rcfError ? (
        <Card padding="lg">
          <EmptyState icon="📊" title="Forecast Unavailable" description="Forecast intelligence is not available for this project." />
        </Card>
      ) : forecastData ? (
        <ForecastIntelligence forecastData={forecastData} />
      ) : null}

      {/* Reference-Class Intelligence */}
      {rcfLoading ? (
        <LoadingState message="Loading reference-class intelligence..." />
      ) : rcfError ? (
        <Card padding="lg">
          <EmptyState icon="📊" title="Reference Class Unavailable" description="No comparable projects are currently available." />
        </Card>
      ) : referenceData ? (
        <ReferenceClassCard referenceData={referenceData} />
      ) : null}

      {/* Risk Journey */}
      {historyLoading ? (
        <LoadingState message="Loading risk history..." />
      ) : historyData && historyData.length > 1 ? (
        <>
          {/* What Changed Section */}
          {historyData.length >= 2 && (
            <Card padding="lg">
              <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.md }}>
                What Changed?
              </h3>
              
              <div style={{ marginBottom: spacing.lg }}>
                <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                  Risk Score
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: spacing.md }}>
                  <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 600, color: colors.text.secondary }}>
                    {historyData[historyData.length - 2].risk_score?.toFixed(1) || 'N/A'}
                  </div>
                  <div style={{ 
                    fontSize: typography.fontSize['2xl'], 
                    fontWeight: 600, 
                    color: (historyData[historyData.length - 1].risk_score - historyData[historyData.length - 2].risk_score) > 0 ? colors.accent.danger : colors.accent.success 
                  }}>
                    →
                  </div>
                  <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 600, color: colors.text.primary }}>
                    {historyData[historyData.length - 1].risk_score?.toFixed(1) || 'N/A'}
                  </div>
                  <div style={{ 
                    padding: `${spacing.xs} ${spacing.sm}`,
                    backgroundColor: (historyData[historyData.length - 1].risk_score - historyData[historyData.length - 2].risk_score) > 0 ? `${colors.accent.danger}10` : `${colors.accent.success}10`,
                    borderRadius: borderRadius.sm,
                    fontSize: typography.fontSize.base,
                    fontWeight: 600,
                    color: (historyData[historyData.length - 1].risk_score - historyData[historyData.length - 2].risk_score) > 0 ? colors.accent.danger : colors.accent.success
                  }}>
                    {(historyData[historyData.length - 1].risk_score - historyData[historyData.length - 2].risk_score) > 0 ? '+' : ''}{(historyData[historyData.length - 1].risk_score - historyData[historyData.length - 2].risk_score)?.toFixed(1)}
                  </div>
                </div>
              </div>

              {/* Associated Driver Changes */}
              <div style={{ 
                padding: spacing.md, 
                backgroundColor: colors.background.tertiary, 
                borderRadius: borderRadius.md 
              }}>
                <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.sm }}>
                  Associated Driver Changes
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xs }}>
                  {riskData?.components && (
                    <>
                      {riskData.components.cost_risk && (
                        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
                          • Cost risk: {riskData.components.cost_risk.toFixed(1)}
                        </div>
                      )}
                      {riskData.components.schedule_risk && (
                        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
                          • Schedule risk: {riskData.components.schedule_risk.toFixed(1)}
                        </div>
                      )}
                      {riskData.components.progress_anomaly_score && (
                        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
                          • Progress anomaly: {riskData.components.progress_anomaly_score.toFixed(1)}
                        </div>
                      )}
                      {riskData.components.governance_risk && (
                        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
                          • Governance risk: {riskData.components.governance_risk.toFixed(1)}
                        </div>
                      )}
                    </>
                  )}
                  <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted, marginTop: spacing.sm }}>
                    * Associated driver changes based on current risk components
                  </div>
                </div>
              </div>
            </Card>
          )}

          <RiskJourney 
            historyData={historyData}
            onPointClick={(point) => {
              setSelectedEvidence({
                risk_score: point.risk_score,
                risk_category: point.risk_category,
                confidence: riskData?.dcs?.dcs_score,
                explanation: `Risk on ${point.month || 'selected date'}`,
                supporting_data: {
                  'Date': point.month,
                  'Risk Score': point.risk_score,
                  'Change': point.change,
                },
                timestamp: point.month,
                source: 'Historical Data',
              });
              setEvidenceDrawerOpen(true);
            }}
          />
        </>
      ) : historyData && historyData.length === 1 ? (
        <Card padding="lg">
          <EmptyState icon="📈" title="Limited Risk History" description="Only one risk observation available. Historical comparison requires at least two data points." />
        </Card>
      ) : (
        <Card padding="lg">
          <EmptyState icon="📈" title="No Risk History" description="Historical risk observations are unavailable for this project." />
        </Card>
      )}

      {/* Data Confidence Score */}
      <DCSCard 
        dcs={riskData?.dcs?.dcs_score || 0}
        trend={riskData?.dcs?.trend}
        components={riskData?.dcs?.components}
        confidenceLabel={riskData?.dcs?.confidence_label}
        warningFlags={riskData?.dcs?.warning_flags}
      />

      {/* Project Timeline */}
      <ProjectTimeline 
        milestones={projectMilestones} 
        currentStage="Execution"
      />

      {/* Governance Status Summary */}
      <Card padding="lg">
        <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
          Governance Status
        </h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: spacing.lg }}>
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Current Stage
            </div>
            <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
              Execution
            </div>
          </div>
          
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Gate
            </div>
            <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
              50% Physical Progress
            </div>
          </div>
          
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Status
            </div>
            <Badge variant="warning" size="md">
              REVIEW REQUIRED
            </Badge>
          </div>
          
          <div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Pending Action
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              Progress milestone review
            </div>
          </div>
        </div>

        {riskData?.components?.governance_risk > 50 && (
          <div style={{ 
            marginTop: spacing.lg, 
            padding: spacing.md, 
            backgroundColor: `${colors.accent.warning}10`, 
            borderRadius: borderRadius.md,
            border: `1px solid ${colors.accent.warning}30`
          }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              ⚠️ Governance risk elevated ({riskData.components.governance_risk.toFixed(1)}). Review recommended.
            </div>
          </div>
        )}
      </Card>

      {/* NID Summary */}
      {nidLoading ? (
        <LoadingState message="Loading narrative intelligence..." />
      ) : nidData ? (
        <NIDSummary nidData={nidData} />
      ) : null}

      {/* PBE Summary */}
      {pbeLoading ? (
        <LoadingState message="Loading peer intelligence..." />
      ) : pbeData ? (
        <PeerBenchmarkSummary pbeData={pbeData} />
      ) : null}

      {/* Recommended Practices (Positive Deviance Radar) */}
      {suggestions && suggestions.suggestions && suggestions.suggestions.length > 0 && (
        <Card padding="lg">
          <h3 style={{
            fontSize: typography.fontSize.lg,
            fontWeight: 600,
            color: colors.text.primary,
            marginBottom: spacing.lg,
          }}>
            Recommended Practices
          </h3>
          <p style={{
            fontSize: typography.fontSize.base,
            color: colors.text.secondary,
            marginBottom: spacing.lg,
          }}>
            Evidence-backed practices from positive deviant projects that may help address this project&apos;s risk drivers.
          </p>
          {suggestionsLoading ? (
            <LoadingState message="Loading recommendations..." />
          ) : suggestionsError ? (
            <div style={{ color: colors.accent.danger }}>Error loading recommendations: {suggestionsError}</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
              {suggestions.suggestions.map((suggestion) => (
                <PlaybookCard
                  key={suggestion.suggestion_id}
                  playbook={{
                    ...suggestion.playbook,
                    suggestion_id: suggestion.suggestion_id,
                  }}
                  triggerReason={suggestion.trigger_reason}
                  onDismiss={dismissSuggestion}
                  onViewed={markSuggestionViewed}
                  isSuggestion={true}
                />
              ))}
            </div>
          )}
        </Card>
      )}

      {/* Anomalies */}
      {riskData?.anomalies && riskData.anomalies.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
          <h3 style={{ 
            fontFamily: typography.fontFamily.sans,
            fontSize: typography.fontSize.lg,
            fontWeight: 600,
            color: colors.text.primary 
          }}>
            Anomalies Detected
          </h3>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(2, 1fr)', 
            gap: spacing.md 
          }}>
            {riskData.anomalies.map((anomaly, index) => (
              <AnomalyCard
                key={index}
                severity={anomaly.severity.toLowerCase()}
                type={anomaly.anomaly_type.replace(/_/g, ' ')}
                observed={anomaly.observed_value}
                expected={anomaly.expected_value}
                delta={anomaly.delta}
                explanation={anomaly.explanation}
                month={anomaly.reporting_period || 'Unknown'}
              />
            ))}
          </div>
        </div>
      )}

      {/* Evidence Drawer */}
      <EvidenceDrawer
        isOpen={evidenceDrawerOpen}
        onClose={() => setEvidenceDrawerOpen(false)}
        evidence={selectedEvidence}
      />
    </div>
  );
}

export default ProjectDetail;

