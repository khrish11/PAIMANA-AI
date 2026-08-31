import { useEffect, useState } from 'react';
import { Card, Badge, Button, DataTable, LoadingState, EmptyState } from '../components/common';
import { colors, spacing, typography, borderRadius } from '../tokens';

function AuditTrail() {
  const [events, setEvents] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    action_type: '',
    entity_type: '',
    entity_id: '',
  });

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/api/v1/audit');
        if (!response.ok) throw new Error('Failed to fetch audit trail');
        const data = await response.json();
        setEvents(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  if (loading) return <LoadingState message="Loading audit trail..." />;
  if (error) return <EmptyState icon="⚠️" title="Error" description={error} />;

  const columns = [
    {
      key: 'timestamp',
      label: 'Timestamp',
      render: (value) => new Date(value).toLocaleString(),
    },
    { key: 'user', label: 'User' },
    { key: 'role', label: 'Role' },
    {
      key: 'action',
      label: 'Action',
      render: (value) => <Badge variant="info" size="sm">{value}</Badge>,
    },
    { key: 'entity_type', label: 'Entity Type' },
    { key: 'entity_id', label: 'Entity ID' },
    {
      key: 'reason',
      label: 'Reason',
      render: (value) => value || '-',
    },
    {
      key: 'details',
      label: 'Details',
      render: () => <Button variant="ghost" size="sm">View Details</Button>,
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {/* Filters */}
      <Card padding="lg">
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(3, 1fr)', 
          gap: spacing.md 
        }}>
          <div>
            <label style={{ 
              display: 'block', 
              fontSize: typography.fontSize.sm, 
              fontWeight: 600,
              color: colors.text.secondary,
              marginBottom: spacing.xs 
            }}>
              Action Type
            </label>
            <select
              value={filters.action_type}
              onChange={(e) => handleFilterChange('action_type', e.target.value)}
              style={{
                width: '100%',
                padding: `${spacing.sm} ${spacing.md}`,
                backgroundColor: colors.background.primary,
                border: `1px solid ${colors.border.default}`,
                borderRadius: borderRadius.md,
                color: colors.text.primary,
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.sm,
              }}
            >
              <option value="">All Actions</option>
              <option value="create_project">Create Project</option>
              <option value="update_project">Update Project</option>
              <option value="cuf_submission">CUF Submission</option>
              <option value="import">Import</option>
              <option value="risk_recalculation">Risk Recalculation</option>
              <option value="governance_action">Governance Action</option>
            </select>
          </div>
          <div>
            <label style={{ 
              display: 'block', 
              fontSize: typography.fontSize.sm, 
              fontWeight: 600,
              color: colors.text.secondary,
              marginBottom: spacing.xs 
            }}>
              Entity Type
            </label>
            <select
              value={filters.entity_type}
              onChange={(e) => handleFilterChange('entity_type', e.target.value)}
              style={{
                width: '100%',
                padding: `${spacing.sm} ${spacing.md}`,
                backgroundColor: colors.background.primary,
                border: `1px solid ${colors.border.default}`,
                borderRadius: borderRadius.md,
                color: colors.text.primary,
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.sm,
              }}
            >
              <option value="">All Entities</option>
              <option value="project">Project</option>
              <option value="submission">Submission</option>
              <option value="import">Import</option>
            </select>
          </div>
          <div>
            <label style={{ 
              display: 'block', 
              fontSize: typography.fontSize.sm, 
              fontWeight: 600,
              color: colors.text.secondary,
              marginBottom: spacing.xs 
            }}>
              Entity ID
            </label>
            <input
              type="text"
              value={filters.entity_id}
              onChange={(e) => handleFilterChange('entity_id', e.target.value)}
              style={{
                width: '100%',
                padding: `${spacing.sm} ${spacing.md}`,
                backgroundColor: colors.background.primary,
                border: `1px solid ${colors.border.default}`,
                borderRadius: borderRadius.md,
                color: colors.text.primary,
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.sm,
              }}
              placeholder="Search by ID..."
            />
          </div>
        </div>
      </Card>

      {/* Audit Events Table */}
      <Card padding="lg">
        <DataTable
          data={events.events.slice(0, 50)}
          columns={columns}
        />
      </Card>

      {/* Pagination */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between' 
      }}>
        <div style={{ 
          fontSize: typography.fontSize.sm, 
          color: colors.text.secondary 
        }}>
          Showing {Math.min(50, events.total_count)} of {events.total_count} events
        </div>
        <div style={{ display: 'flex', gap: spacing.sm }}>
          <Button variant="ghost" size="sm">Previous</Button>
          <Button variant="ghost" size="sm">Next</Button>
        </div>
      </div>
    </div>
  );
}

export default AuditTrail;
