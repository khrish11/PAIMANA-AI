import { useState } from 'react';
import { Card, Button } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function BlastRadiusPanel({ projectId, fetchBlastRadius }) {
  const [depth, setDepth] = useState(2);
  const [riskThreshold, setRiskThreshold] = useState('HIGH');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!projectId) {
      setError('Project ID is required');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const blastData = await fetchBlastRadius(depth, null, riskThreshold);
      setResult(blastData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card padding="lg">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Network Reach Analysis (Blast Radius)
      </h3>

      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
          Analysis Depth
        </div>
        <div style={{ display: 'flex', gap: spacing.sm }}>
          {[1, 2, 3].map(d => (
            <button
              key={d}
              onClick={() => setDepth(d)}
              style={{
                padding: `${spacing.xs} ${spacing.sm}`,
                fontSize: typography.fontSize.sm,
                backgroundColor: depth === d ? colors.accent.primary : colors.background.secondary,
                color: depth === d ? 'white' : colors.text.primary,
                border: `1px solid ${depth === d ? colors.accent.primary : colors.border.light}`,
                borderRadius: '0.25rem',
                cursor: 'pointer'
              }}
            >
              {d} hop{d > 1 ? 's' : ''}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
          Risk Threshold
        </div>
        <select
          value={riskThreshold}
          onChange={(e) => setRiskThreshold(e.target.value)}
          style={{
            padding: spacing.sm,
            fontSize: typography.fontSize.base,
            backgroundColor: colors.background.secondary,
            border: `1px solid ${colors.border.light}`,
            borderRadius: '0.25rem',
            color: colors.text.primary,
            width: '100%'
          }}
        >
          <option value="ALL">All Risk Levels</option>
          <option value="HIGH">HIGH and above</option>
          <option value="VERY_HIGH">VERY_HIGH and above</option>
          <option value="CRITICAL">CRITICAL only</option>
        </select>
      </div>

      <Button onClick={handleAnalyze} disabled={loading || !projectId}>
        {loading ? 'Analyzing...' : 'Analyze Network Reach'}
      </Button>

      {error && (
        <div style={{ 
          marginTop: spacing.lg,
          padding: spacing.md,
          backgroundColor: `${colors.accent.danger}10`,
          borderRadius: '0.375rem',
          border: `1px solid ${colors.accent.danger}30`,
          color: colors.accent.danger
        }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: spacing.lg }}>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.md }}>
            <strong>NOTE:</strong> This is network reachability analysis, not impact propagation. It identifies which nodes are reachable within {depth} hop(s).
          </div>

          <div style={{ marginBottom: spacing.md }}>
            <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
              Affected Nodes: {result.affected_nodes?.length || 0}
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              Total nodes reachable within {depth} hop(s)
            </div>
          </div>

          <div style={{ marginBottom: spacing.md }}>
            <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
              Affected Projects: {result.affected_projects?.length || 0}
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              Projects in the reachable network
            </div>
          </div>

          <div style={{ marginBottom: spacing.md }}>
            <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
              Affected Agencies: {result.affected_agencies?.length || 0}
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              Agencies in the reachable network
            </div>
          </div>

          <div style={{ marginBottom: spacing.md }}>
            <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
              Affected States: {result.affected_states?.length || 0}
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              States in the reachable network
            </div>
          </div>

          <div style={{ marginBottom: spacing.md }}>
            <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
              Affected Sectors: {result.affected_sectors?.length || 0}
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              Sectors in the reachable network
            </div>
          </div>

          {result.dependency_paths && result.dependency_paths.length > 0 && (
            <div style={{ marginTop: spacing.lg }}>
              <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
                Dependency Paths ({result.dependency_paths.length})
              </div>
              <div style={{ maxHeight: '200px', overflowY: 'auto', fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
                {result.dependency_paths.slice(0, 20).map((path, index) => (
                  <div key={index} style={{ padding: spacing.xs, borderBottom: `1px solid ${colors.border.light}` }}>
                    {path.from} → {path.to} ({path.relationship}, depth {path.depth})
                  </div>
                ))}
                {result.dependency_paths.length > 20 && (
                  <div style={{ padding: spacing.xs, color: colors.text.muted }}>
                    ... and {result.dependency_paths.length - 20} more paths
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
