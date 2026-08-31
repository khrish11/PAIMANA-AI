import { useParams, useState } from 'react';
import { Card, Button, LoadingState, EmptyState } from '../components/common';
import { 
  PeerPosition, 
  PeerCriteria, 
  PeerBenchmarkSummary, 
  PeerGapAnalysis, 
  BenchmarkMethodology 
} from '../components/pbe';
import { EvidenceDrawer, EvidenceMetadata, IntelligenceHeader } from '../components/intelligence';
import { usePBE } from '../hooks';
import { spacing } from '../tokens';

function PeerIntelligence() {
  const { id } = useParams();
  const [evidenceDrawerOpen, setEvidenceDrawerOpen] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState(null);

  const { data: pbeData, loading, error, retry } = usePBE(id);

  const handleInvestigate = () => {
    if (pbeData) {
      setSelectedEvidence({
        title: 'Peer Benchmark Evidence',
        risk_score: pbeData.ppi_score,
        risk_category: pbeData.percentile >= 80 ? 'EXCELLENT' : pbeData.percentile >= 60 ? 'GOOD' : 'NEEDS IMPROVEMENT',
        confidence: 'HIGH',
        explanation: pbeData.explanation,
        supporting_data: {
          'PPI Score': pbeData.ppi_score?.toFixed(0),
          'Percentile': `${pbeData.percentile?.toFixed(0)}th`,
          'Cohort Size': pbeData.cohort_size,
          'Cohort Sector': pbeData.cohort_sector,
          'Cohort Size Band': pbeData.cohort_size_band,
          'Cost Variance': `${(pbeData.peer_relative_cost_variance * 100).toFixed(1)}%`,
          'Schedule Variance': `${pbeData.peer_relative_schedule_variance?.toFixed(1)} months`,
          'Reporting Quality': pbeData.peer_reporting_quality?.toFixed(0),
        },
        timestamp: new Date().toISOString(),
        source: 'PBE Service',
      });
      setEvidenceDrawerOpen(true);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: spacing.xl }}>
        <LoadingState message="Loading peer intelligence..." />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: spacing.xl }}>
        <Card padding="lg">
          <EmptyState 
            icon="⚠️" 
            title="Peer Intelligence Unavailable" 
            description="We couldn't retrieve the peer benchmark." 
          />
          <Button variant="primary" size="md" onClick={retry} style={{ marginTop: spacing.md }}>
            Retry
          </Button>
        </Card>
      </div>
    );
  }

  if (!pbeData) {
    return (
      <div style={{ padding: spacing.xl }}>
        <Card padding="lg">
          <EmptyState 
            icon="📊" 
            title="PBE Analysis Unavailable" 
            description="The PBE service did not return an analysis." 
          />
        </Card>
      </div>
    );
  }

  return (
    <div style={{ padding: spacing.xl, maxWidth: '100%', overflow: 'hidden' }}>
      {/* Intelligence Header */}
      <IntelligenceHeader
        title="PEER INTELLIGENCE"
        subtitle="Understand how this project performs against comparable projects."
        status={pbeData.percentile >= 80 ? 'EXCELLENT' : pbeData.percentile >= 60 ? 'GOOD' : 'NEEDS IMPROVEMENT'}
        timestamp={new Date().toISOString()}
        confidence="HIGH"
        actions={[
          { label: 'Back to Project', variant: 'secondary', size: 'sm', onClick: () => window.location.href = `/projects/${id}` },
          { label: 'Investigate', variant: 'primary', size: 'sm', onClick: handleInvestigate },
        ]}
      />

      {/* Peer Position */}
      <PeerPosition pbeData={pbeData} />

      {/* Peer Criteria */}
      <PeerCriteria pbeData={pbeData} />

      {/* Peer Benchmark Summary */}
      <PeerBenchmarkSummary pbeData={pbeData} />

      {/* Peer Gap Analysis */}
      <PeerGapAnalysis pbeData={pbeData} />

      {/* Benchmark Methodology */}
      <BenchmarkMethodology />

      {/* Evidence Drawer */}
      {evidenceDrawerOpen && selectedEvidence && (
        <EvidenceDrawer
          isOpen={evidenceDrawerOpen}
          onClose={() => setEvidenceDrawerOpen(false)}
          evidence={selectedEvidence}
        >
          <EvidenceMetadata
            model="PBE Service v1"
            predictionTimestamp={new Date().toISOString()}
            lastDataUpdate={new Date().toISOString()}
            confidence="HIGH"
            source="PBE Service"
          />
        </EvidenceDrawer>
      )}
    </div>
  );
}

export default PeerIntelligence;
