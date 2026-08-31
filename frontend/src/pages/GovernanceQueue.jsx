import { useEffect, useState } from 'react';
import { getProjects } from '../services/api';
import { Card, Badge, Button, DataTable, LoadingState, EmptyState } from '../components/common';
import { KPICard } from '../components/domain';
import { colors, spacing, typography } from '../tokens';

function GovernanceQueue() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [action, setAction] = useState('');

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await getProjects({ risk_category: 'HIGH' });
        setData(response);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const handleAction = (projectId, actionType) => {
    setSelectedProject(projectId);
    setAction(actionType);
    console.log(`Initiating ${actionType} for project ${projectId}`);
  };

  if (loading) return <LoadingState message="Loading governance queue..." />;
  if (error) return <EmptyState icon="⚠️" title="Error" description={error} />;

  const highRiskProjects = data.projects.filter(p => 
    p.risk_category === 'HIGH' || p.risk_category === 'VERY_HIGH' || p.risk_category === 'CRITICAL'
  );

  const criticalCount = highRiskProjects.filter(p => p.risk_category === 'CRITICAL').length;
  const avgDCS = (highRiskProjects.reduce((sum, p) => sum + (p.dcs_score || 0), 0) / highRiskProjects.length || 0).toFixed(1);

  const columns = [
    {
      key: 'project_name',
      label: 'Project',
      render: (value, row) => (
        <div>
          <div style={{ fontWeight: 600 }}>{value}</div>
          <div style={{ fontSize: '0.875rem', color: colors.text.muted }}>{row.project_id}</div>
        </div>
      ),
    },
    {
      key: 'risk_score',
      label: 'Risk Score',
      render: (value) => value?.toFixed(1) || 'N/A',
    },
    {
      key: 'risk_category',
      label: 'Risk Category',
      render: (value) => (
        <Badge
          variant={
            value === 'CRITICAL' ? 'critical' :
            value === 'VERY_HIGH' ? 'danger' : 'warning'
          }
          size="sm"
        >
          {value}
        </Badge>
      ),
    },
    {
      key: 'dcs_score',
      label: 'DCS',
      render: (value) => value?.toFixed(1) || 'N/A',
    },
    {
      key: 'model_status',
      label: 'Model Status',
      render: () => <Badge variant="warning" size="sm">Experimental</Badge>,
    },
    {
      key: 'last_updated',
      label: 'Date Triggered',
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (_, row) => (
        <div style={{ display: 'flex', gap: spacing.xs }}>
          <Button variant="primary" size="sm" onClick={() => handleAction(row.project_id, 'review')}>
            Review
          </Button>
          <Button variant="ghost" size="sm" onClick={() => handleAction(row.project_id, 'defer')}>
            Defer
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {/* Queue Stats */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)', 
        gap: spacing.md 
      }}>
        <KPICard
          label="Projects in Queue"
          value={highRiskProjects.length}
          icon="📋"
        />
        <KPICard
          label="Critical Projects"
          value={criticalCount}
          icon="🚨"
          trendDirection="up"
        />
        <KPICard
          label="Average DCS"
          value={avgDCS}
          icon="💚"
        />
      </div>

      {/* Project Queue */}
      <Card padding="lg">
        <DataTable
          data={highRiskProjects}
          columns={columns}
        />
      </Card>

      {/* Action Confirmation Modal */}
      {selectedProject && (
        <div style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <Card padding="lg" style={{ maxWidth: '400px', width: '100%', margin: spacing.md }}>
            <h3 style={{ 
              fontSize: typography.fontSize.lg,
              fontWeight: 600,
              marginBottom: spacing.md 
            }}>
              Confirm {action}
            </h3>
            <p style={{ 
              fontSize: typography.fontSize.sm,
              color: colors.text.secondary,
              marginBottom: spacing.lg 
            }}>
              You are about to {action} project {selectedProject}. This action will be recorded in the governance audit log.
            </p>
            <div style={{ display: 'flex', gap: spacing.md }}>
              <Button
                variant="ghost"
                onClick={() => {
                  setSelectedProject(null);
                  setAction('');
                }}
                style={{ flex: 1 }}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  setSelectedProject(null);
                  setAction('');
                }}
                style={{ flex: 1 }}
              >
                Confirm
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

export default GovernanceQueue;
