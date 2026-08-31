import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects } from '../services/api';
import { Card, Badge, Button, DataTable, LoadingState, EmptyState } from '../components/common';
import { colors, spacing, typography, borderRadius } from '../tokens';

function ProjectList() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    risk_category: '',
    sector: '',
    state: '',
    ministry: ''
  });

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await getProjects(filters);
        setData(response);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [filters]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleRowClick = (project) => {
    navigate(`/projects/${project.project_id}`);
  };

  if (loading) return <LoadingState message="Loading projects..." />;
  if (error) return <EmptyState icon="⚠️" title="Error" description={error} />;

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
    { key: 'sector', label: 'Sector' },
    { key: 'state', label: 'State' },
    {
      key: 'risk_score',
      label: 'ML Risk',
      render: (value) => value?.toFixed(1) || 'N/A',
    },
    {
      key: 'risk_category',
      label: 'Risk Category',
      render: (value) => (
        <Badge
          variant={
            value === 'CRITICAL' ? 'critical' :
            value === 'VERY_HIGH' ? 'danger' :
            value === 'HIGH' ? 'warning' :
            value === 'MODERATE' ? 'info' : 'success'
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
      key: 'anomaly_count',
      label: 'Anomalies',
      render: (value) => value || '0',
    },
    {
      key: 'model_status',
      label: 'Model Status',
      render: () => <Badge variant="warning" size="sm">Experimental</Badge>,
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
      {/* Filters */}
      <Card padding="lg">
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(4, 1fr)', 
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
              Risk Category
            </label>
            <select
              value={filters.risk_category}
              onChange={(e) => handleFilterChange('risk_category', e.target.value)}
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
              <option value="">All</option>
              <option value="LOW">Low</option>
              <option value="MODERATE">Moderate</option>
              <option value="HIGH">High</option>
              <option value="VERY_HIGH">Very High</option>
              <option value="CRITICAL">Critical</option>
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
              Sector
            </label>
            <select
              value={filters.sector}
              onChange={(e) => handleFilterChange('sector', e.target.value)}
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
              <option value="">All</option>
              <option value="Roads">Roads</option>
              <option value="Railways">Railways</option>
              <option value="Power">Power</option>
              <option value="Water">Water</option>
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
              State
            </label>
            <select
              value={filters.state}
              onChange={(e) => handleFilterChange('state', e.target.value)}
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
              <option value="">All</option>
              <option value="Maharashtra">Maharashtra</option>
              <option value="Karnataka">Karnataka</option>
              <option value="Tamil Nadu">Tamil Nadu</option>
              <option value="Gujarat">Gujarat</option>
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
              Ministry
            </label>
            <select
              value={filters.ministry}
              onChange={(e) => handleFilterChange('ministry', e.target.value)}
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
              <option value="">All</option>
              <option value="Ministry of Road Transport">Road Transport</option>
              <option value="Ministry of Railways">Railways</option>
              <option value="Ministry of Power">Power</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Project Table */}
      <Card padding="lg">
        <DataTable
          data={data.projects || []}
          columns={columns}
          onRowClick={handleRowClick}
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
          Showing {data.projects?.length || 0} of {data.total_count || 0} projects
        </div>
        <div style={{ display: 'flex', gap: spacing.sm }}>
          <Button variant="ghost" size="sm">Previous</Button>
          <Button variant="ghost" size="sm">Next</Button>
        </div>
      </div>
    </div>
  );
}

export default ProjectList;
