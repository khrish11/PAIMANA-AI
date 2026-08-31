import { useState } from 'react';
import { useNetworkIntelligence } from '../hooks';
import { 
  NetworkGraph, 
  NodeDetails, 
  EdgeDetails, 
  BlastRadiusPanel, 
  CriticalDependencies, 
  RiskClusters, 
  NetworkHotspots, 
  NetworkTable, 
  NetworkFilters 
} from '../components/network';
import { Card, LoadingState, Button } from '../components/common';
import { colors, spacing, typography } from '../tokens';

function NetworkExplorer() {
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [viewMode, setViewMode] = useState('graph'); // 'graph' or 'table'
  const [filteredNodes, setFilteredNodes] = useState(null);

  const {
    data,
    loading,
    error,
    available,
    nodes,
    edges,
    metadata,
    fetchBlastRadius,
    retry
  } = useNetworkIntelligence();

  const handleFilter = (filters) => {
    let filtered = [...nodes];
    
    if (filters.nodeType !== 'ALL') {
      filtered = filtered.filter(n => n.node_type === filters.nodeType);
    }
    
    if (filters.riskCategory !== 'ALL') {
      filtered = filtered.filter(n => n.risk_category === filters.riskCategory);
    }
    
    setFilteredNodes(filtered);
  };

  const displayNodes = filteredNodes || nodes;

  if (loading) return <LoadingState message="Loading network data..." />;

  if (error) {
    return (
      <div style={{ padding: spacing.xl }}>
        <Card padding="xl">
          <div style={{ textAlign: 'center' }}>
            <h2 style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.danger, marginBottom: spacing.md }}>
              Network Loading Failed
            </h2>
            <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary, marginBottom: spacing.lg }}>
              {error}
            </p>
            <Button onClick={retry}>Retry</Button>
          </div>
        </Card>
      </div>
    );
  }

  if (!available) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
        <Card padding="lg">
          <h2 style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary, marginBottom: spacing.md }}>
            NETWORK INTELLIGENCE
          </h2>
          <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary, marginBottom: spacing.lg }}>
            Understand project dependencies, relationships and systemic exposure.
          </p>
          
          <div style={{ 
            padding: spacing.lg, 
            backgroundColor: `${colors.accent.warning}10`, 
            borderRadius: '0.5rem',
            border: `1px solid ${colors.accent.warning}30`,
            marginBottom: spacing.lg
          }}>
            <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
              NETWORK ANALYSIS UNAVAILABLE
            </h3>
            <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary, marginBottom: spacing.md }}>
              {data?.message || "The Network Intelligence backend is not yet implemented."}
            </p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {/* Header */}
      <Card padding="lg">
        <h2 style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary, marginBottom: spacing.md }}>
          NETWORK INTELLIGENCE
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary, marginBottom: spacing.lg }}>
          Understand project dependencies, relationships and systemic exposure.
        </p>

        {/* Network Summary */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: spacing.md }}>
          <div style={{ padding: spacing.md, backgroundColor: colors.background.tertiary, borderRadius: '0.375rem', border: `1px solid ${colors.border.light}` }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>Total Projects</div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
              {metadata.total_projects || 0}
            </div>
          </div>
          <div style={{ padding: spacing.md, backgroundColor: colors.background.tertiary, borderRadius: '0.375rem', border: `1px solid ${colors.border.light}` }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>Connected Projects</div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
              {nodes.filter(n => n.node_type === 'PROJECT').length}
            </div>
          </div>
          <div style={{ padding: spacing.md, backgroundColor: colors.background.tertiary, borderRadius: '0.375rem', border: `1px solid ${colors.border.light}` }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>High-Risk Nodes</div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.accent.danger }}>
              {metadata.high_risk_projects || 0}
            </div>
          </div>
          <div style={{ padding: spacing.md, backgroundColor: colors.background.tertiary, borderRadius: '0.375rem', border: `1px solid ${colors.border.light}` }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>Agencies</div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
              {metadata.total_agencies || 0}
            </div>
          </div>
          <div style={{ padding: spacing.md, backgroundColor: colors.background.tertiary, borderRadius: '0.375rem', border: `1px solid ${colors.border.light}` }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>States</div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
              {metadata.total_states || 0}
            </div>
          </div>
          <div style={{ padding: spacing.md, backgroundColor: colors.background.tertiary, borderRadius: '0.375rem', border: `1px solid ${colors.border.light}` }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>Sectors</div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
              {metadata.total_sectors || 0}
            </div>
          </div>
        </div>

        {/* View Mode Toggle */}
        <div style={{ marginTop: spacing.lg, display: 'flex', gap: spacing.sm }}>
          <button
            onClick={() => setViewMode('graph')}
            style={{
              padding: `${spacing.sm} ${spacing.md}`,
              fontSize: typography.fontSize.base,
              backgroundColor: viewMode === 'graph' ? colors.accent.primary : colors.background.secondary,
              color: viewMode === 'graph' ? 'white' : colors.text.primary,
              border: `1px solid ${viewMode === 'graph' ? colors.accent.primary : colors.border.light}`,
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            Graph View
          </button>
          <button
            onClick={() => setViewMode('table')}
            style={{
              padding: `${spacing.sm} ${spacing.md}`,
              fontSize: typography.fontSize.base,
              backgroundColor: viewMode === 'table' ? colors.accent.primary : colors.background.secondary,
              color: viewMode === 'table' ? 'white' : colors.text.primary,
              border: `1px solid ${viewMode === 'table' ? colors.accent.primary : colors.border.light}`,
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            Table View
          </button>
        </div>
      </Card>

      {/* Main Content */}
      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr 300px', gap: spacing.lg }}>
        {/* Left Sidebar - Filters */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
          <NetworkFilters nodes={nodes} onFilter={handleFilter} />
          <RiskClusters nodes={displayNodes} edges={edges} />
          <NetworkHotspots nodes={displayNodes} edges={edges} />
        </div>

        {/* Center - Graph or Table */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
          {viewMode === 'graph' ? (
            <NetworkGraph 
              nodes={displayNodes} 
              edges={edges} 
              onNodeClick={setSelectedNode}
              onEdgeClick={setSelectedEdge}
              selectedNode={selectedNode}
              selectedEdge={selectedEdge}
            />
          ) : (
            <NetworkTable 
              nodes={displayNodes} 
              edges={edges} 
              onNodeClick={setSelectedNode}
            />
          )}
          <CriticalDependencies edges={edges} nodes={displayNodes} />
        </div>

        {/* Right Sidebar - Details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
          <NodeDetails node={selectedNode} onClose={() => setSelectedNode(null)} />
          <EdgeDetails edge={selectedEdge} onClose={() => setSelectedEdge(null)} />
          <BlastRadiusPanel projectId={selectedNode?.node_type === 'PROJECT' ? selectedNode.id : null} fetchBlastRadius={fetchBlastRadius} />
        </div>
      </div>

      {/* Bottom - Dependency Paths */}
      {selectedNode && (
        <BlastRadiusPanel projectId={selectedNode.node_type === 'PROJECT' ? selectedNode.id : null} fetchBlastRadius={fetchBlastRadius} />
      )}
    </div>
  );
}

export default NetworkExplorer;
