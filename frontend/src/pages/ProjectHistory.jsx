import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getProjectHistory } from '../services/api';
import { Card, Badge, Button, LoadingState, EmptyState } from '../components/common';
import { colors, spacing, typography, borderRadius } from '../tokens';

function ProjectHistory() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchHistory() {
      try {
        const response = await getProjectHistory(id);
        setData(response);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
  }, [id]);

  const getVersionBadge = (version, isLatest, supersededBy) => {
    if (supersededBy) {
      return <Badge variant="secondary" size="sm">v{version} (Superseded)</Badge>;
    }
    if (isLatest) {
      return <Badge variant="success" size="sm">v{version} (Latest)</Badge>;
    }
    return <Badge variant="info" size="sm">v{version}</Badge>;
  };

  if (loading) return <LoadingState message="Loading project history..." />;
  if (error) return <EmptyState icon="⚠️" title="Error" description={error} />;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.primary }}>
            Project History
          </h1>
          <p style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, marginTop: spacing.xs }}>
            {data?.project_name} ({data?.project_code})
          </p>
        </div>
        <div style={{ display: 'flex', gap: spacing.sm }}>
          <Button variant="secondary" onClick={() => navigate(`/projects/${id}`)}>
            Back to Project
          </Button>
          <Button variant="primary" onClick={() => navigate('/data-entry')}>
            Add Monthly CUF
          </Button>
        </div>
      </div>

      {/* Summary */}
      <Card padding="md">
        <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary }}>
          Total Submissions: {data?.total_submissions || 0}
        </div>
      </Card>

      {/* History Timeline */}
      {data?.history && data.history.length > 0 ? (
        <Card padding="lg">
          <h2 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
            Submission Timeline
          </h2>
          
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: `1px solid ${colors.border.default}` }}>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Reporting Month
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Version
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Physical Progress
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Expenditure (₹ Cr)
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Revised Cost (₹ Cr)
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Planned Completion
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Submitted By
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Submitted At
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Data Source
                  </th>
                  <th style={{ padding: spacing.md, textAlign: 'left', fontSize: typography.fontSize.xs, fontWeight: 600, color: colors.text.secondary }}>
                    Superseded
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.history.map((submission) => (
                  <tr key={submission.submission_id} style={{ borderBottom: `1px solid ${colors.border.default}` }}>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {submission.reporting_month ? new Date(submission.reporting_month).toLocaleDateString() : 'N/A'}
                    </td>
                    <td style={{ padding: spacing.md }}>
                      {getVersionBadge(submission.version, submission.is_latest, submission.superseded_by)}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {submission.physical_progress !== null ? `${submission.physical_progress.toFixed(1)}%` : 'N/A'}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {submission.expenditure !== null ? `₹${submission.expenditure.toFixed(2)}` : 'N/A'}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {submission.revised_cost !== null ? `₹${submission.revised_cost.toFixed(2)}` : 'N/A'}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {submission.planned_completion ? new Date(submission.planned_completion).toLocaleDateString() : 'N/A'}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {submission.submitted_by || 'N/A'}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {submission.submitted_at ? new Date(submission.submitted_at).toLocaleString() : 'N/A'}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {submission.data_source || 'N/A'}
                    </td>
                    <td style={{ padding: spacing.md, fontSize: typography.fontSize.sm, color: colors.text.primary }}>
                      {submission.superseded_by ? (
                        <div>
                          <div style={{ fontSize: typography.fontSize.xs, color: colors.text.secondary }}>
                            Yes at {submission.superseded_at ? new Date(submission.superseded_at).toLocaleString() : 'N/A'}
                          </div>
                          {submission.superseded_reason && (
                            <div style={{ fontSize: typography.fontSize.xs, color: colors.accent.warning }}>
                              Reason: {submission.superseded_reason}
                            </div>
                          )}
                        </div>
                      ) : (
                        'No'
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : (
        <Card padding="lg">
          <EmptyState 
            icon="📅" 
            title="No History Found" 
            description="No submission history is available for this project." 
          />
        </Card>
      )}

      {/* Narrative History */}
      {data?.history && data.history.filter(h => h.narrative_text).length > 0 && (
        <Card padding="lg">
          <h2 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
            Narrative History
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
            {data.history
              .filter(h => h.narrative_text)
              .map((submission) => (
                <div 
                  key={submission.submission_id}
                  style={{ 
                    padding: spacing.md,
                    backgroundColor: colors.background.tertiary,
                    borderRadius: borderRadius.md,
                    border: `1px solid ${colors.border.default}`
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: spacing.sm }}>
                    <div style={{ fontSize: typography.fontSize.sm, fontWeight: 600, color: colors.text.primary }}>
                      {submission.reporting_month ? new Date(submission.reporting_month).toLocaleDateString() : 'N/A'}
                    </div>
                    {getVersionBadge(submission.version, submission.is_latest, submission.superseded_by)}
                  </div>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, lineHeight: 1.5 }}>
                    {submission.narrative_text}
                  </div>
                </div>
              ))}
          </div>
        </Card>
      )}
    </div>
  );
}

export default ProjectHistory;
