import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, LoadingState, EmptyState, Button } from '../components/common';
import { usePositiveDeviance } from '../hooks';
import { colors, spacing, typography } from '../tokens';

function PositiveDeviance() {
  const [filters, setFilters] = useState({
    sector: null,
    state: null,
  });

  const {
    positiveDeviants,
    loading,
    error,
    fetchPositiveDeviants,
    retry,
  } = usePositiveDeviance();

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value || null };
    setFilters(newFilters);
    fetchPositiveDeviants(newFilters);
  };

  if (loading) return <LoadingState message="Loading positive deviants..." />;

  if (error) {
    return (
      <div style={{ padding: spacing.xl }}>
        <Card padding="xl">
          <div style={{ textAlign: 'center' }}>
            <h2 style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.danger, marginBottom: spacing.md }}>
              Positive Deviants Loading Failed
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

  if (!positiveDeviants || positiveDeviants.positive_deviants.length === 0) {
    return (
      <div style={{ padding: spacing.xl }}>
        <Card padding="xl">
          <EmptyState
            icon="🎯"
            title="No Positive Deviants Detected"
            description="Positive deviants are projects performing significantly better than their reference class. None have been detected yet."
          />
        </Card>
      </div>
    );
  }

  const deviants = positiveDeviants.positive_deviants;
  const metadata = positiveDeviants.metadata || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {/* Header */}
      <Card padding="lg">
        <h2 style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary, marginBottom: spacing.md }}>
          POSITIVE DEVIANCE RADAR
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary, marginBottom: spacing.lg }}>
          Projects performing significantly better than their reference class peers
        </p>

        {/* Summary Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: spacing.md }}>
          <div style={{ padding: spacing.md, backgroundColor: colors.background.tertiary, borderRadius: '0.375rem', border: `1px solid ${colors.border.light}` }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>Total Deviants</div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
              {deviants.length}
            </div>
          </div>
          <div style={{ padding: spacing.md, backgroundColor: colors.background.tertiary, borderRadius: '0.375rem', border: `1px solid ${colors.border.light}` }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>Sectors</div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
              {metadata.sectors || 0}
            </div>
          </div>
          <div style={{ padding: spacing.md, backgroundColor: colors.background.tertiary, borderRadius: '0.375rem', border: `1px solid ${colors.border.light}` }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>States</div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
              {metadata.states || 0}
            </div>
          </div>
          <div style={{ padding: spacing.md, backgroundColor: colors.background.tertiary, borderRadius: '0.375rem', border: `1px solid ${colors.border.light}` }}>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>High DCS</div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.accent.success }}>
              {deviants.filter(d => d.data_confidence_score >= 80).length}
            </div>
          </div>
        </div>

        {/* Filters */}
        <div style={{ marginTop: spacing.lg, display: 'flex', gap: spacing.md, flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '200px' }}>
            <label style={{ display: 'block', fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
              Sector
            </label>
            <select
              value={filters.sector || ''}
              onChange={(e) => handleFilterChange('sector', e.target.value)}
              style={{
                width: '100%',
                padding: spacing.sm,
                fontSize: typography.fontSize.base,
                color: colors.text.primary,
                backgroundColor: colors.background.primary,
                border: `1px solid ${colors.border.light}`,
                borderRadius: '0.25rem',
              }}
            >
              <option value="">All Sectors</option>
              {[...new Set(deviants.map(d => d.sector).filter(Boolean))].map(sector => (
                <option key={sector} value={sector}>{sector}</option>
              ))}
            </select>
          </div>

          <div style={{ flex: 1, minWidth: '200px' }}>
            <label style={{ display: 'block', fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
              State
            </label>
            <select
              value={filters.state || ''}
              onChange={(e) => handleFilterChange('state', e.target.value)}
              style={{
                width: '100%',
                padding: spacing.sm,
                fontSize: typography.fontSize.base,
                color: colors.text.primary,
                backgroundColor: colors.background.primary,
                border: `1px solid ${colors.border.light}`,
                borderRadius: '0.25rem',
              }}
            >
              <option value="">All States</option>
              {[...new Set(deviants.map(d => d.state).filter(Boolean))].map(state => (
                <option key={state} value={state}>{state}</option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {/* Deviants Table */}
      <Card padding="lg">
        <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
          Positive Deviants
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: `2px solid ${colors.border.light}` }}>
                <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.muted }}>
                  Project
                </th>
                <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.muted }}>
                  Sector
                </th>
                <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.muted }}>
                  State
                </th>
                <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.muted }}>
                  Reference Class
                </th>
                <th style={{ padding: spacing.md, textAlign: 'right', fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.muted }}>
                  Cost Residual
                </th>
                <th style={{ padding: spacing.md, textAlign: 'right', fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.muted }}>
                  Schedule Residual
                </th>
                <th style={{ padding: spacing.md, textAlign: 'right', fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.muted }}>
                  DCS
                </th>
                <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.muted }}>
                  Detected
                </th>
              </tr>
            </thead>
            <tbody>
              {deviants.map((deviant) => (
                <tr
                  key={deviant.deviant_id}
                  style={{ borderBottom: `1px solid ${colors.border.light}`, cursor: 'pointer' }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = colors.background.tertiary;
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = 'transparent';
                  }}
                >
                  <td style={{ padding: spacing.md }}>
                    <Link
                      to={`/projects/${deviant.project_id}`}
                      style={{ 
                        color: colors.accent.primary, 
                        textDecoration: 'none',
                        fontWeight: 500,
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.textDecoration = 'underline';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.textDecoration = 'none';
                      }}
                    >
                      {deviant.project_name || deviant.project_id}
                    </Link>
                  </td>
                  <td style={{ padding: spacing.md, color: colors.text.secondary }}>
                    {deviant.sector || 'N/A'}
                  </td>
                  <td style={{ padding: spacing.md, color: colors.text.secondary }}>
                    {deviant.state || 'N/A'}
                  </td>
                  <td style={{ padding: spacing.md, color: colors.text.secondary }}>
                    {deviant.reference_class_id || 'N/A'}
                  </td>
                  <td style={{ padding: spacing.md, textAlign: 'right', color: deviant.residual_cost_zscore < 0 ? colors.accent.success : colors.text.secondary }}>
                    {deviant.residual_cost_zscore?.toFixed(2) || 'N/A'}
                  </td>
                  <td style={{ padding: spacing.md, textAlign: 'right', color: deviant.residual_schedule_zscore < 0 ? colors.accent.success : colors.text.secondary }}>
                    {deviant.residual_schedule_zscore?.toFixed(2) || 'N/A'}
                  </td>
                  <td style={{ padding: spacing.md, textAlign: 'right', color: colors.text.secondary }}>
                    {deviant.data_confidence_score?.toFixed(0) || 'N/A'}
                  </td>
                  <td style={{ padding: spacing.md, color: colors.text.muted, fontSize: typography.fontSize.sm }}>
                    {new Date(deviant.detected_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Methodology Note */}
      <Card padding="lg" style={{ backgroundColor: `${colors.accent.primary}05`, border: `1px solid ${colors.accent.primary}20` }}>
        <h4 style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.sm }}>
          Methodology
        </h4>
        <p style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, marginBottom: spacing.sm }}>
          A project is identified as a positive deviant when:
        </p>
        <ul style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, paddingLeft: spacing.lg, marginBottom: 0 }}>
          <li>Its reference class has sufficient sample size (≥15 projects)</li>
          <li>Performance is materially better than the class (negative residual z-score)</li>
          <li>It has at least 6 months of tracking history</li>
          <li>Data confidence score (DCS) meets minimum threshold (≥70)</li>
        </ul>
      </Card>
    </div>
  );
}

export default PositiveDeviance;
