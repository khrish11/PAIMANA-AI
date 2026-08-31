import { useParams, useState } from 'react';
import { Card, Button, LoadingState, EmptyState } from '../components/common';
import { 
  NQCGauge, 
  ContradictionCard, 
  ClaimEvidenceMap, 
  NIDSummary 
} from '../components/nid';
import { EvidenceDrawer, EvidenceMetadata, IntelligenceHeader } from '../components/intelligence';
import { useNID } from '../hooks';
import { colors, spacing, typography } from '../tokens';

function NarrativeIntelligence() {
  const { id } = useParams();
  const [evidenceDrawerOpen, setEvidenceDrawerOpen] = useState(false);
  const [selectedContradiction, setSelectedContradiction] = useState(null);
  const [severityFilter, setSeverityFilter] = useState('ALL');

  const { data: nidData, loading, error, retry } = useNID(id);

  const handleInvestigate = (contradiction) => {
    setSelectedContradiction(contradiction);
    setEvidenceDrawerOpen(true);
  };

  const filteredContradictions = nidData?.contradictions?.filter(c => 
    severityFilter === 'ALL' || c.severity === severityFilter
  ) || [];

  if (loading) {
    return (
      <div style={{ padding: spacing.xl }}>
        <LoadingState message="Loading narrative intelligence..." />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: spacing.xl }}>
        <Card padding="lg">
          <EmptyState 
            icon="⚠️" 
            title="NID Intelligence Unavailable" 
            description="We couldn't retrieve narrative intelligence." 
          />
          <Button variant="primary" size="md" onClick={retry} style={{ marginTop: spacing.md }}>
            Retry
          </Button>
        </Card>
      </div>
    );
  }

  if (!nidData) {
    return (
      <div style={{ padding: spacing.xl }}>
        <Card padding="lg">
          <EmptyState 
            icon="📝" 
            title="NID Analysis Unavailable" 
            description="The NID service did not return an analysis." 
          />
        </Card>
      </div>
    );
  }

  return (
    <div style={{ padding: spacing.xl, maxWidth: '100%', overflow: 'hidden' }}>
      {/* Intelligence Header */}
      <IntelligenceHeader
        title="NARRATIVE INTELLIGENCE"
        subtitle="Detect inconsistencies between reported progress and quantitative project evidence."
        status={nidData.nqc_score >= 80 ? 'GOOD' : nidData.nqc_score >= 60 ? 'MODERATE' : 'POOR'}
        timestamp={new Date().toISOString()}
        confidence={nidData.confidence}
        actions={[
          { label: 'Back to Project', variant: 'secondary', size: 'sm', onClick: () => window.location.href = `/projects/${id}` },
        ]}
      />

      {/* NQC Score */}
      <NQCGauge nqcScore={nidData.nqc_score} confidence={nidData.confidence} />

      {/* NID Summary */}
      <NIDSummary nidData={nidData} />

      {/* Contradictions Section */}
      <div style={{ marginTop: spacing.xl }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.lg }}>
          <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary }}>
            Contradictions Detected
          </h3>
          <div style={{ display: 'flex', gap: spacing.sm }}>
            {['ALL', 'CRITICAL', 'HIGH', 'MODERATE', 'LOW'].map(severity => (
              <Button
                key={severity}
                variant={severityFilter === severity ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setSeverityFilter(severity)}
              >
                {severity}
              </Button>
            ))}
          </div>
        </div>

        {filteredContradictions.length === 0 ? (
          <Card padding="lg">
            <EmptyState 
              icon="✓" 
              title="No Contradictions Detected" 
              description={`Current narrative and quantitative evidence show no detected contradictions matching ${severityFilter} severity.`} 
            />
          </Card>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: spacing.lg }}>
            {filteredContradictions.map((contradiction, index) => (
              <ContradictionCard 
                key={index} 
                contradiction={contradiction} 
                onInvestigate={handleInvestigate} 
              />
            ))}
          </div>
        )}
      </div>

      {/* Evidence Drawer */}
      {evidenceDrawerOpen && selectedContradiction && (
        <EvidenceDrawer
          isOpen={evidenceDrawerOpen}
          onClose={() => setEvidenceDrawerOpen(false)}
          evidence={{
            title: 'NID Evidence',
            risk_score: nidData.nqc_score,
            risk_category: nidData.nqc_score >= 80 ? 'GOOD' : nidData.nqc_score >= 60 ? 'MODERATE' : 'POOR',
            confidence: nidData.confidence,
            explanation: selectedContradiction.explanation,
            supporting_data: {
              'Narrative Claim': selectedContradiction.claim,
              'Referenced Field': selectedContradiction.referenced_cuf_field,
              'Expected Value': selectedContradiction.expected_value,
              'Actual Value': selectedContradiction.actual_value,
              'Coherence Score': selectedContradiction.coherence_score?.toFixed(2),
              'Severity': selectedContradiction.severity,
            },
            timestamp: new Date().toISOString(),
            source: 'NID Analysis',
          }}
        >
          <ClaimEvidenceMap contradiction={selectedContradiction} />
          <EvidenceMetadata
            model={nidData.model_version}
            predictionTimestamp={new Date().toISOString()}
            lastDataUpdate={new Date().toISOString()}
            confidence={nidData.confidence}
            source="NID Service"
          />
        </EvidenceDrawer>
      )}
    </div>
  );
}

export default NarrativeIntelligence;
