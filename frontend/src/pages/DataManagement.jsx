import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects } from '../services/api';
import { Card, Badge, Button, DataTable, LoadingState, EmptyState } from '../components/common';
import { KPICard } from '../components/domain';
import { colors, spacing, typography, borderRadius } from '../tokens';

function DataManagement() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    risk_category: '',
    sector: '',
    state: '',
    ministry: '',
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

  if (loading) return <LoadingState message="Loading data management..." />;
  if (error) return <EmptyState icon="⚠️" title="Error" description={error} />;

  const projectsRequiringUpdate = data.projects.filter(p => p.dcs_score < 70).length;
  const lowDcsProjects = data.projects.filter(p => p.dcs_score < 50).length;

  const columns = [
    { key: 'project_id', label: 'Project ID' },
    { key: 'project_name', label: 'Project Name' },
    { key: 'ministry', label: 'Ministry' },
    { key: 'sector', label: 'Sector' },
    { key: 'state', label: 'State' },
    {
      key: 'sanctioned_cost',
      label: 'Sanctioned Cost',
      render: (value) => value ? `₹${value.toFixed(0)} Cr` : 'N/A',
    },
    {
      key: 'revised_cost',
      label: 'Revised Cost',
      render: (value) => value ? `₹${value.toFixed(0)} Cr` : 'N/A',
    },
    {
      key: 'physical_progress',
      label: 'Physical Progress',
      render: (value) => value ? `${value.toFixed(1)}%` : 'N/A',
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => <Badge variant="info" size="sm">{value || 'ongoing'}</Badge>,
    },
    {
      key: 'risk_score',
      label: 'Risk',
      render: (value) => value?.toFixed(1) || 'N/A',
    },
    {
      key: 'dcs_score',
      label: 'DCS',
      render: (value) => value?.toFixed(1) || 'N/A',
    },
    { key: 'last_updated', label: 'Last Updated' },
    {
      key: 'actions',
      label: 'Actions',
      render: (_, row) => (
        <div style={{ display: 'flex', gap: spacing.xs }}>
          <Button variant="primary" size="sm" onClick={() => handleRowClick(row)}>
            View
          </Button>
          <Button variant="ghost" size="sm">
            Edit
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {/* Action Buttons */}
      <Card padding="md">
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: spacing.sm }}>
          <Button variant="primary" onClick={() => navigate('/data-management/new-project')}>
            Add Project
          </Button>
          <Button variant="secondary" onClick={() => navigate('/data-entry')}>
            Add Monthly Update
          </Button>
          <Button variant="secondary" onClick={() => navigate('/data-import')}>
            Import CSV/XLSX
          </Button>
          <Button variant="ghost">
            Generate Report
          </Button>
        </div>
      </Card>

      {/* KPI Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(4, 1fr)', 
        gap: spacing.md 
      }}>
        <KPICard
          label="Total Projects"
          value={data.projects.length}
          icon="🏗️"
        />
        <KPICard
          label="Monthly Submissions"
          value={data.projects.length * 6}
          icon="📊"
        />
        <KPICard
          label="Projects Requiring Update"
          value={projectsRequiringUpdate}
          icon="⚠️"
          trendDirection="up"
        />
        <KPICard
          label="Low-DCS Projects"
          value={lowDcsProjects}
          icon="🚨"
          trendDirection="up"
        />
      </div>

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
          data={data.projects.slice(0, 20)}
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
          Showing {Math.min(20, data.projects.length)} of {data.total_count} projects
        </div>
        <div style={{ display: 'flex', gap: spacing.sm }}>
          <Button variant="ghost" size="sm">Previous</Button>
          <Button variant="ghost" size="sm">Next</Button>
        </div>
      </div>
    </div>
  );
}

export default DataManagement;
