import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';
import { memo } from 'react';

function PeerBenchmarkSummary({ pbeData }) {
  if (!pbeData) {
    return (
      <Card padding="lg" role="region" aria-label="Peer Benchmark Summary">
        <div style={{ textAlign: 'center', color: colors.text.muted }}>
          Benchmark summary unavailable
        </div>
      </Card>
    );
  }

  const metrics = [
    {
      label: 'PPI Score',
      value: pbeData.ppi_score?.toFixed(0) || 'N/A',
      description: 'Peer Performance Index (0-100)',
    },
    {
      label: 'Percentile',
      value: `${pbeData.percentile?.toFixed(0) || 'N/A'}th`,
      description: 'Position within peer cohort',
    },
    {
      label: 'Cost Variance',
      value: `${(pbeData.peer_relative_cost_variance * 100).toFixed(1)}%`,
      description: 'Relative to peer median',
    },
    {
      label: 'Schedule Variance',
      value: `${pbeData.peer_relative_schedule_variance?.toFixed(1) || 'N/A'} months`,
      description: 'Relative to peer median',
    },
    {
      label: 'Reporting Quality',
      value: `${pbeData.peer_reporting_quality?.toFixed(0) || 'N/A'}`,
      description: 'Peer-relative quality score',
    },
  ];

  return (
    <Card padding="lg" role="region" aria-label="Peer Benchmark Summary">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        PEER BENCHMARK SUMMARY
      </h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: spacing.lg }}>
        {metrics.map((metric, index) => (
          <div key={index}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              {metric.label}
            </div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
              {metric.value}
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
              {metric.description}
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: spacing.lg, paddingTop: spacing.md, borderTop: `1px solid ${colors.border.default}` }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
          COHORT RANGE
        </div>
        <div style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Min: {(pbeData.cohort_range_min * 100).toFixed(1)}% | Max: {(pbeData.cohort_range_max * 100).toFixed(1)}%
        </div>
      </div>
    </Card>
  );
}

export default memo(PeerBenchmarkSummary);
