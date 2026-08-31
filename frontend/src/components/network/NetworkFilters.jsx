import { useState } from 'react';
import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';

export default function NetworkFilters({ onFilter }) {
  const [nodeType, setNodeType] = useState('ALL');
  const [riskCategory, setRiskCategory] = useState('ALL');

  const nodeTypes = ['ALL', 'PROJECT', 'AGENCY', 'STATE', 'SECTOR'];
  const riskCategories = ['ALL', 'LOW', 'MODERATE', 'HIGH', 'VERY_HIGH', 'CRITICAL'];

  const handleFilterChange = () => {
    if (onFilter) {
      onFilter({ nodeType, riskCategory });
    }
  };

  return (
    <Card padding="lg">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Network Filters
      </h3>

      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
          Node Type
        </div>
        <select
          value={nodeType}
          onChange={(e) => {
            setNodeType(e.target.value);
            handleFilterChange();
          }}
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
          {nodeTypes.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: spacing.lg }}>
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
          Risk Category
        </div>
        <select
          value={riskCategory}
          onChange={(e) => {
            setRiskCategory(e.target.value);
            handleFilterChange();
          }}
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
          {riskCategories.map(risk => (
            <option key={risk} value={risk}>{risk}</option>
          ))}
        </select>
      </div>

      <button
        onClick={() => {
          setNodeType('ALL');
          setRiskCategory('ALL');
          if (onFilter) onFilter({ nodeType: 'ALL', riskCategory: 'ALL' });
        }}
        style={{
          padding: `${spacing.sm} ${spacing.md}`,
          fontSize: typography.fontSize.base,
          backgroundColor: colors.background.secondary,
          border: `1px solid ${colors.border.light}`,
          borderRadius: '0.25rem',
          cursor: 'pointer',
          color: colors.text.primary,
          width: '100%'
        }}
      >
        Reset Filters
      </button>
    </Card>
  );
}
