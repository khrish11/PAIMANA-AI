import { useParams, useNavigate } from 'react-router-dom';
import { useProjectIntelligence } from '../hooks';
import { 
  DecisionSummary, 
  SignalOverview, 
  IntelligenceCorrelation, 
  SignalConvergence,
  EvidenceChain,
  WhatChanged,
  IntelligenceTimeline,
  AttentionQueue,
  DecisionReadiness,
  ModelTransparency,
  ProvenancePanel,
  IntelligenceMap
} from '../components/intelligence';
import { Card, Button, LoadingState } from '../components/common';
import { colors, spacing, typography } from '../tokens';

export default function ProjectIntelligence() {
  const { id: projectId } = useParams();
  const navigate = useNavigate();
  
  const {
    data,
    loading,
    error,
    availability,
    retry,
  } = useProjectIntelligence(projectId);

  const risk = data.risk;

  // Overall loading state
  if (loading.overall) {
    return (
      <div style={{ padding: spacing.xl }}>
        <LoadingState message="Loading project intelligence..." />
      </div>
    );
  }

  // Overall error state
  if (error.overall) {
    return (
      <div style={{ padding: spacing.xl }}>
        <Card padding="xl">
          <div style={{ textAlign: 'center' }}>
            <h2 style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.danger, marginBottom: spacing.md }}>
              Intelligence Loading Failed
            </h2>
            <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary, marginBottom: spacing.lg }}>
              {error.overall}
            </p>
            <Button onClick={retry}>Retry</Button>
            <Button variant="secondary" onClick={() => navigate('/projects')}>
              Back to Projects
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ padding: spacing.xl, backgroundColor: colors.background.primary, minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ marginBottom: spacing.xl }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: spacing.md }}>
          <div>
            <h1 style={{ fontSize: typography.fontSize['3xl'], fontWeight: 700, color: colors.text.primary, marginBottom: spacing.xs }}>
              PROJECT INTELLIGENCE
            </h1>
            <p style={{ fontSize: typography.fontSize.lg, color: colors.text.secondary }}>
              Unified evidence, risk, forecast and benchmark intelligence.
            </p>
          </div>
          <div style={{ display: 'flex', gap: spacing.sm }}>
            <Button variant="secondary" onClick={() => navigate(`/projects/${projectId}/decision-cockpit`)}>
              Open Decision Cockpit
            </Button>
            <Button variant="secondary" onClick={() => navigate('/projects')}>
              Back to Projects
            </Button>
          </div>
        </div>

        {/* Project Context */}
        {risk && (
          <div style={{ 
            padding: spacing.lg,
            backgroundColor: colors.background.secondary,
            borderRadius: '0.5rem',
            border: `1px solid ${colors.border.light}`,
            display: 'flex',
            gap: spacing.xl,
            flexWrap: 'wrap'
          }}>
            <div>
              <span style={{ color: colors.text.muted, fontSize: typography.fontSize.sm }}>Project: </span>
              <span style={{ fontWeight: 600, color: colors.text.primary }}>{risk.project_name || 'N/A'}</span>
            </div>
            <div>
              <span style={{ color: colors.text.muted, fontSize: typography.fontSize.sm }}>ID: </span>
              <span style={{ fontWeight: 600, color: colors.text.primary }}>{projectId}</span>
            </div>
            <div>
              <span style={{ color: colors.text.muted, fontSize: typography.fontSize.sm }}>Sector: </span>
              <span style={{ fontWeight: 600, color: colors.text.primary }}>{risk.sector || 'N/A'}</span>
            </div>
            <div>
              <span style={{ color: colors.text.muted, fontSize: typography.fontSize.sm }}>State: </span>
              <span style={{ fontWeight: 600, color: colors.text.primary }}>{risk.state || 'N/A'}</span>
            </div>
            <div>
              <span style={{ color: colors.text.muted, fontSize: typography.fontSize.sm }}>Status: </span>
              <span style={{ fontWeight: 600, color: colors.text.primary }}>{risk.status || 'N/A'}</span>
            </div>
            <div>
              <span style={{ color: colors.text.muted, fontSize: typography.fontSize.sm }}>Updated: </span>
              <span style={{ fontWeight: 600, color: colors.text.primary }}>{risk.reporting_month || 'N/A'}</span>
            </div>
          </div>
        )}

        {/* Intelligence Layers Status */}
        <div style={{ marginTop: spacing.md, display: 'flex', gap: spacing.sm, flexWrap: 'wrap' }}>
          <span style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
            Intelligence Layers:
          </span>
          <span style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: availability.risk === 'available' ? colors.accent.success : colors.text.muted }}>
            Risk {availability.risk === 'available' ? '✓' : '—'}
          </span>
          <span style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: availability.nid === 'available' ? colors.accent.success : colors.text.muted }}>
            NID {availability.nid === 'available' ? '✓' : '—'}
          </span>
          <span style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: availability.pbe === 'available' ? colors.accent.success : colors.text.muted }}>
            PBE {availability.pbe === 'available' ? '✓' : '—'}
          </span>
          <span style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: availability.rcf === 'available' ? colors.accent.success : colors.text.muted }}>
            Forecast {availability.rcf === 'available' ? '✓' : '—'}
          </span>
          <span style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: availability.risk === 'available' ? colors.accent.success : colors.text.muted }}>
            DCS {availability.risk === 'available' ? '✓' : '—'}
          </span>
          <span style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: availability.network === 'available' ? colors.accent.success : colors.text.muted }}>
            Network {availability.network === 'available' ? '✓' : '—'}
          </span>
        </div>
      </div>

      {/* Main Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: spacing.lg, marginBottom: spacing.xl }}>
        {/* Decision Summary */}
        <div style={{ gridColumn: '1 / -1' }}>
          <DecisionSummary intelligence={{ data, availability }} />
        </div>

        {/* Signal Overview */}
        <div style={{ gridColumn: '1 / -1' }}>
          <SignalOverview intelligence={{ data, availability }} />
        </div>

        {/* Intelligence Map */}
        <div style={{ gridColumn: '1 / -1' }}>
          <IntelligenceMap intelligence={{ data, availability }} projectId={projectId} />
        </div>

        {/* Signal Convergence */}
        <div>
          <SignalConvergence intelligence={{ data, availability }} />
        </div>

        {/* Intelligence Correlation */}
        <div>
          <IntelligenceCorrelation intelligence={{ data, availability }} />
        </div>

        {/* Evidence Chain */}
        <div style={{ gridColumn: '1 / -1' }}>
          <EvidenceChain intelligence={{ data, availability }} />
        </div>

        {/* What Changed */}
        <div>
          <WhatChanged intelligence={{ data, availability }} />
        </div>

        {/* Intelligence Timeline */}
        <div>
          <IntelligenceTimeline intelligence={{ data, availability }} />
        </div>

        {/* Attention Queue */}
        <div style={{ gridColumn: '1 / -1' }}>
          <AttentionQueue intelligence={{ data, availability }} />
        </div>

        {/* Decision Readiness */}
        <div>
          <DecisionReadiness intelligence={{ data, availability }} />
        </div>

        {/* Model Transparency */}
        <div>
          <ModelTransparency intelligence={{ data, availability }} />
        </div>

        {/* Provenance Panel */}
        <div style={{ gridColumn: '1 / -1' }}>
          <ProvenancePanel intelligence={{ data, availability }} />
        </div>
      </div>

      {/* Footer */}
      <div style={{ 
        padding: spacing.lg,
        backgroundColor: colors.background.secondary,
        borderRadius: '0.5rem',
        border: `1px solid ${colors.border.light}`,
        textAlign: 'center',
        fontSize: typography.fontSize.sm,
        color: colors.text.muted
      }}>
        <div style={{ marginBottom: spacing.sm }}>
          <strong>INTELLIGENCE → DECISION WORKFLOW:</strong> Project → Intelligence → Evidence → Signals → Risk → Forecast → Peer Position → Network → Decision Cockpit → What-If Simulation
        </div>
        <div>
          All intelligence data is backend-authoritative. No fabricated values or correlations are displayed.
        </div>
      </div>
    </div>
  );
}
