import React, { useState } from 'react';
import { colors, spacing, typography } from '../../tokens';
import PlaybookCard from './PlaybookCard';

function PlaybookLibrary({ playbooks, loading, error, onFilterChange }) {
  const [filters, setFilters] = useState({
    category: 'ALL',
    confidence_tier: 'ALL',
  });

  const categories = ['ALL', 'land_acquisition', 'procurement', 'contractor_management', 'design_change', 'stakeholder_coordination', 'resource_planning', 'other'];
  const confidenceTiers = ['ALL', 'LOW', 'MEDIUM', 'HIGH'];

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    if (onFilterChange) {
      onFilterChange(newFilters);
    }
  };

  const filteredPlaybooks = playbooks?.filter(playbook => {
    if (filters.category !== 'ALL' && playbook.category !== filters.category) return false;
    if (filters.confidence_tier !== 'ALL' && playbook.confidence_tier !== filters.confidence_tier) return false;
    return true;
  }) || [];

  if (loading) {
    return (
      <div style={{ padding: spacing.xl, textAlign: 'center' }}>
        <div style={{ color: colors.text.muted }}>Loading playbook library...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: spacing.xl, textAlign: 'center' }}>
        <div style={{ color: colors.accent.danger }}>Error loading playbooks: {error}</div>
      </div>
    );
  }

  return (
    <div style={{ padding: spacing.xl }}>
      {/* Header */}
      <div style={{ marginBottom: spacing.xl }}>
        <h2 style={{
          fontSize: typography.fontSize['2xl'],
          fontWeight: 700,
          color: colors.text.primary,
          marginBottom: spacing.md,
        }}>
          Playbook Library
        </h2>
        <p style={{
          fontSize: typography.fontSize.base,
          color: colors.text.secondary,
        }}>
          Evidence-backed practices extracted from positive deviant projects
        </p>
      </div>

      {/* Filters */}
      <div style={{
        display: 'flex',
        gap: spacing.lg,
        padding: spacing.lg,
        backgroundColor: colors.background.secondary,
        borderRadius: '0.5rem',
        border: `1px solid ${colors.border.light}`,
        marginBottom: spacing.xl,
        flexWrap: 'wrap',
      }}>
        <div style={{ flex: 1, minWidth: '200px' }}>
          <label
            htmlFor="category-filter"
            style={{
              display: 'block',
              fontSize: typography.fontSize.sm,
              fontWeight: 600,
              color: colors.text.primary,
              marginBottom: spacing.sm,
            }}
          >
            Category
          </label>
          <select
            id="category-filter"
            value={filters.category}
            onChange={(e) => handleFilterChange('category', e.target.value)}
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
            {categories.map(cat => (
              <option key={cat} value={cat}>
                {cat === 'ALL' ? 'All Categories' : cat.replace('_', ' ')}
              </option>
            ))}
          </select>
        </div>

        <div style={{ flex: 1, minWidth: '200px' }}>
          <label
            htmlFor="confidence-filter"
            style={{
              display: 'block',
              fontSize: typography.fontSize.sm,
              fontWeight: 600,
              color: colors.text.primary,
              marginBottom: spacing.sm,
            }}
          >
            Confidence Tier
          </label>
          <select
            id="confidence-filter"
            value={filters.confidence_tier}
            onChange={(e) => handleFilterChange('confidence_tier', e.target.value)}
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
            {confidenceTiers.map(tier => (
              <option key={tier} value={tier}>
                {tier === 'ALL' ? 'All Tiers' : tier}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Results Count */}
      <div style={{
        fontSize: typography.fontSize.sm,
        color: colors.text.muted,
        marginBottom: spacing.lg,
      }}>
        Showing {filteredPlaybooks.length} of {playbooks?.length || 0} playbooks
      </div>

      {/* Playbooks Grid */}
      {filteredPlaybooks.length === 0 ? (
        <div style={{
          padding: spacing.xl,
          textAlign: 'center',
          backgroundColor: colors.background.secondary,
          borderRadius: '0.5rem',
          border: `1px solid ${colors.border.light}`,
        }}>
          <div style={{ color: colors.text.muted }}>No playbooks match the selected filters</div>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
          gap: spacing.lg,
        }}>
          {filteredPlaybooks.map(playbook => (
            <PlaybookCard
              key={playbook.playbook_id}
              playbook={playbook}
              isSuggestion={false}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default PlaybookLibrary;
