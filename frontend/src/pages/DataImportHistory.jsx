import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getImportBatches } from '../services/api';
import { Card, Badge, Button, LoadingState, EmptyState } from '../components/common';
import { colors, spacing, typography, borderRadius } from '../tokens';

function DataImportHistory() {
  const navigate = useNavigate();
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    async function fetchBatches() {
      try {
        const response = await getImportBatches(statusFilter, 50);
        setBatches(response.batches || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchBatches();
  }, [statusFilter]);

  const getStatusBadge = (status) => {
    const variant = status === 'completed' ? 'success' : status === 'failed' ? 'danger' : 'warning';
    return <Badge variant={variant} size="sm">{status}</Badge>;
  };

  if (loading) return <LoadingState message="Loading import history..." />;
  if (error) return <EmptyState icon="⚠️" title="Error" description={error} />;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
            Import History
          </h1>
          <p style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, marginTop: spacing.xs }}>
            View all bulk import operations
          </p>
        </div>
        <Button variant="primary" onClick={() => navigate('/data-import')}>
          New Import
        </Button>
      </div>

      {/* Filters */}
      <Card padding="md">
        <div style={{ display: 'flex', gap: spacing.md, alignItems: 'center' }}>
          <label style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.secondary }}>
            Status:
          </label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              padding: `${spacing.sm} ${spacing.md}`,
              backgroundColor: colors.background.primary,
              border: `1px solid ${colors.border.default}`,
              borderRadius: borderRadius.md,
              color: colors.text.primary,
              fontFamily: typography.fontFamily.sans,
              fontSize: typography.fontSize.sm,
            }}
          >
            <option value="">All</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="in_progress">In Progress</option>
          </select>
        </div>
      </Card>

      {/* Batches Table */}
      <Card padding="lg">
        {batches.length === 0 ? (
          <EmptyState icon="📦" title="No imports found" description="No import batches match the current filter" />
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: `1px solid ${colors.border.default}` }}>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Batch ID
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Batch Name
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Status
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Rows
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    New Projects
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    New Submissions
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Revisions
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Invalid
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Created By
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Completed At
                  </th>
                </tr>
              </thead>
              <tbody>
                {batches.map((batch) => (
                  <tr key={batch.batch_id} style={{ borderBottom: `1px solid ${colors.border.default}` }}>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {batch.batch_id.slice(0, 8)}...
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {batch.batch_name}
                    </td>
                    <td style={{ padding: spacing.md }}>
                      {getStatusBadge(batch.status)}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {batch.rows_detected}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {batch.new_projects}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {batch.new_submissions}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {batch.revisions}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {batch.invalid_rows}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {batch.created_by}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {batch.completed_at ? new Date(batch.completed_at).toLocaleString() : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Summary */}
      <Card padding="md">
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
          Showing {batches.length} import batches
        </div>
      </Card>
    </div>
  );
}

export default DataImportHistory;
