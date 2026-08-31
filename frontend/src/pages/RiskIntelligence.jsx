import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Badge, Button, DataTable, LoadingState, EmptyState } from '../components/common';
import { KPICard } from '../components/domain';
import { 
  EvidenceDrawer, 
  RiskBreakdown, 
  RiskJourney, 
  ReferenceClassCard, 
  ForecastIntelligence, 
  IntelligenceFeed, 
  RiskMovement 
} from '../components/intelligence';
import { useRiskIntelligence, useRiskHistory, useForecast, useReferenceClass } from '../hooks';
import { colors, spacing, typography, borderRadius, shadows } from '../tokens';

function RiskIntelligence() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState({
    risk_category: '',
    sector: '',
    state: '',
    agency: '',
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProject, setSelectedProject] = useState(null);
  const [evidenceDrawerOpen, setEvidenceDrawerOpen] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState(null);

  const { data: intelligenceData, loading: intelligenceLoading, error: intelligenceError, retry: retryIntelligence } = useRiskIntelligence(filters);
  const { data: riskHistory } = useRiskHistory(selectedProject);
  const { data: forecastData } = useForecast(selectedProject);
  const { data: referenceClassData } = useReferenceClass(selectedProject);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleProjectClick = (projectId) => {
    setSelectedProject(projectId);
    navigate(`/projects/${projectId}`);
  };

  const handleWhyClick = (project) => {
    setSelectedEvidence({
      risk_score: project.risk_score,
      risk_category: project.risk_category,
      confidence: project.confidence,
      shap_drivers: project.shap_drivers,
      explanation: project.explanation,
      supporting_data: project.supporting_data,
      timestamp: project.last_updated,
      model_version: project.model_version,
    });
    setEvidenceDrawerOpen(true);
  };

  const handleRiskCategoryClick = (category) => {
    setFilters(prev => ({ ...prev, risk_category: category }));
  };

  const handleSearch = (e) => {
    setSearchQuery(e.target.value);
  };

  if (intelligenceLoading) {
    return <LoadingState message="Loading risk intelligence..." />;
  }

  if (intelligenceError) {
    return (
      <EmptyState 
        icon="⚠️" 
        title="Risk Intelligence Unavailable" 
        description="We couldn't retrieve the current risk intelligence."
      >
        <Button variant="primary" onClick={retryIntelligence}>Retry</Button>
      </EmptyState>
    );
  }

  const dashboard = intelligenceData?.dashboard;
  const projects = intelligenceData?.projects || [];

  // Calculate risk distribution
  const riskDistribution = {
    LOW: projects.filter(p => p.risk_category === 'LOW').length,
    MODERATE: projects.filter(p => p.risk_category === 'MODERATE').length,
    HIGH: projects.filter(p => p.risk_category === 'HIGH').length,
    VERY_HIGH: projects.filter(p => p.risk_category === 'VERY_HIGH').length,
    CRITICAL: projects.filter(p => p.risk_category === 'CRITICAL').length,
  };

  // Filter projects based on search and filters
  const filteredProjects = projects.filter(project => {
    const matchesSearch = !searchQuery || 
      project.project_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.project_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.ministry?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.sector?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.state?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesFilters = 
      (!filters.risk_category || project.risk_category === filters.risk_category) &&
      (!filters.sector || project.sector === filters.sector) &&
      (!filters.state || project.state === filters.state) &&
      (!filters.agency || project.implementing_agency === filters.agency);

    return matchesSearch && matchesFilters;
  });

  // Critical projects
  const criticalProjects = filteredProjects.filter(p => p.risk_category === 'CRITICAL' || p.risk_category === 'VERY_HIGH');

  // Mock risk movements (would come from backend in production)
  const riskMovements = criticalProjects.slice(0, 5).map(p => ({
    project_id: p.project_id,
    project_name: p.project_name,
    previous_risk: p.risk_score - (Math.random() * 10 - 5),
    current_risk: p.risk_score,
    change: Math.random() * 10 - 5,
    primary_driver: p.top_driver || 'Schedule delay',
    timestamp: new Date(Date.now() - Math.random() * 86400000).toISOString(),
  }));

  // Mock intelligence feed events
  const intelligenceEvents = [
    ...criticalProjects.slice(0, 3).map(p => ({
      severity: 'CRITICAL',
      event_type: 'Project risk crossed threshold',
      project_name: p.project_name,
      project_id: p.project_id,
      explanation: `Risk score for ${p.project_name} has reached critical level`,
      timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
    })),
    {
      severity: 'WARNING',
      event_type: 'Narrative inconsistency detected',
      project_name: projects[0]?.project_name || 'Unknown',
      project_id: projects[0]?.project_id,
      explanation: 'Discrepancy between reported progress and physical observations',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
    },
    {
      severity: 'DATA',
      event_type: 'CUF submission stale',
      project_name: projects[1]?.project_name || 'Unknown',
      project_id: projects[1]?.project_id,
      explanation: 'Monthly update not submitted for 45 days',
      timestamp: new Date(Date.now() - 10800000).toISOString(),
    },
  ];

  const criticalColumns = [
    {
      key: 'project_name',
      label: 'Project',
      render: (value, row) => (
        <div>
          <div style={{ fontWeight: 600, color: colors.text.primary }}>{value}</div>
          <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>{row.project_id}</div>
        </div>
      ),
    },
    { key: 'sector', label: 'Sector' },
    { key: 'state', label: 'State' },
    {
      key: 'risk_score',
      label: 'Risk',
      render: (value) => (
        <div style={{ fontSize: typography.fontSize.lg, fontWeight: 700, color: colors.text.primary }}>
          {value?.toFixed(1) || 'N/A'}
        </div>
      ),
    },
    {
      key: 'risk_category',
      label: 'Category',
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
      key: 'confidence',
      label: 'Confidence',
      render: (value) => value?.toFixed(0) || 'N/A',
    },
    {
      key: 'top_driver',
      label: 'Primary Driver',
      render: (value) => value || 'N/A',
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (_, row) => (
        <Button variant="primary" size="sm" onClick={() => handleProjectClick(row.project_id)}>
          Investigate
        </Button>
      ),
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {/* Intelligence Header */}
      <div style={{ 
        padding: spacing.xl, 
        backgroundColor: colors.background.secondary, 
        borderRadius: borderRadius.lg,
        border: `1px solid ${colors.border.default}`
      }}>
        <h1 style={{ fontSize: typography.fontSize['3xl'], fontWeight: 700, color: colors.text.primary, marginBottom: spacing.sm }}>
          RISK INTELLIGENCE
        </h1>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary, marginBottom: spacing.lg }}>
          National infrastructure early-warning center
        </p>

        {/* Header KPIs */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(6, 1fr)', 
          gap: spacing.md 
        }}>
          <KPICard
            label="Active Projects"
            value={dashboard?.kpi?.total_projects || 'N/A'}
            icon="🏗️"
          />
          <KPICard
            label="Critical Projects"
            value={riskDistribution.CRITICAL}
            icon="🚨"
            trendDirection="up"
          />
          <KPICard
            label="Very High Risk"
            value={riskDistribution.VERY_HIGH}
            icon="⚠️"
            trendDirection="up"
          />
          <KPICard
            label="High Risk"
            value={riskDistribution.HIGH}
            icon="🔶"
            trendDirection="up"
          />
          <KPICard
            label="Active Alerts"
            value={dashboard?.alerts?.length || 0}
            icon="🔔"
            trendDirection="up"
          />
          <KPICard
            label="Data Confidence"
            value={dashboard?.kpi?.avg_dcs?.toFixed(0) || 'N/A'}
            icon="💎"
          />
        </div>
      </div>

      {/* Filters and Search */}
      <Card padding="lg">
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(5, 1fr)', 
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
              Search
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearch}
              placeholder="Project ID, name, sector..."
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
            />
          </div>
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
              <option value="">All Categories</option>
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
              <option value="">All Sectors</option>
              {[...new Set(projects.map(p => p.sector))].map(sector => (
                <option key={sector} value={sector}>{sector}</option>
              ))}
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
              <option value="">All States</option>
              {[...new Set(projects.map(p => p.state))].map(state => (
                <option key={state} value={state}>{state}</option>
              ))}
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
              Agency
            </label>
            <select
              value={filters.agency}
              onChange={(e) => handleFilterChange('agency', e.target.value)}
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
              <option value="">All Agencies</option>
              {[...new Set(projects.map(p => p.implementing_agency))].map(agency => (
                <option key={agency} value={agency}>{agency}</option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {/* National Risk Summary */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(4, 1fr)', 
        gap: spacing.md 
      }}>
        <KPICard
          label="Total Active Projects"
          value={filteredProjects.length}
          icon="📊"
        />
        <KPICard
          label="Average Risk"
          value={dashboard?.kpi?.avg_composite_risk?.toFixed(1) || 'N/A'}
          icon="📈"
        />
        <KPICard
          label="Risk Increased"
          value={Math.floor(filteredProjects.length * 0.15)}
          icon="📈"
          trendDirection="up"
        />
        <KPICard
          label="Risk Decreased"
          value={Math.floor(filteredProjects.length * 0.10)}
          icon="📉"
          trendDirection="down"
        />
      </div>

      {/* Risk Distribution */}
      <Card padding="lg">
        <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
          Risk Distribution
        </h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(5, 1fr)', 
          gap: spacing.md 
        }}>
          {[
            { label: 'LOW', count: riskDistribution.LOW, color: colors.risk.low },
            { label: 'MODERATE', count: riskDistribution.MODERATE, color: colors.risk.medium },
            { label: 'HIGH', count: riskDistribution.HIGH, color: colors.risk.high },
            { label: 'VERY HIGH', count: riskDistribution.VERY_HIGH, color: colors.risk.high },
            { label: 'CRITICAL', count: riskDistribution.CRITICAL, color: colors.risk.critical },
          ].map((category) => (
            <div
              key={category.label}
              onClick={() => handleRiskCategoryClick(category.label)}
              style={{
                padding: spacing.lg,
                backgroundColor: colors.background.tertiary,
                borderRadius: borderRadius.md,
                cursor: 'pointer',
                transition: 'all 150ms ease-in-out',
                border: `2px solid ${category.color}`,
                textAlign: 'center',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = shadows.md;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div style={{ fontSize: typography.fontSize['3xl'], fontWeight: 700, color: category.color }}>
                {category.count}
              </div>
              <div style={{ fontSize: typography.fontSize.sm, color: colors.text.secondary, marginTop: spacing.xs }}>
                {category.label}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Main Content Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '2fr 1fr', 
        gap: spacing.lg 
      }}>
        {/* Left Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
          {/* Critical Project Monitor */}
          <Card padding="lg">
            <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
              Critical Project Monitor
            </h3>
            {criticalProjects.length > 0 ? (
              <DataTable
                data={criticalProjects.slice(0, 10)}
                columns={criticalColumns}
              />
            ) : (
              <EmptyState icon="✅" title="No Critical Projects" description="No projects currently meet the critical-risk threshold." />
            )}
          </Card>

          {/* Risk Movement */}
          <RiskMovement 
            movements={riskMovements} 
            onInvestigate={handleProjectClick} 
          />
        </div>

        {/* Right Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
          {/* Intelligence Feed */}
          <IntelligenceFeed 
            events={intelligenceEvents} 
            onProjectClick={handleProjectClick} 
          />

          {/* Selected Project Details */}
          {selectedProject && (
            <>
              <RiskBreakdown 
                riskData={projects.find(p => p.project_id === selectedProject)} 
                onWhyClick={() => handleWhyClick(projects.find(p => p.project_id === selectedProject))}
              />
              
              <RiskJourney 
                historyData={riskHistory}
                onPointClick={(point) => console.log('Selected point:', point)}
              />

              <ForecastIntelligence forecastData={forecastData} />

              <ReferenceClassCard referenceData={referenceClassData} />
            </>
          )}
        </div>
      </div>

      {/* Evidence Drawer */}
      <EvidenceDrawer
        isOpen={evidenceDrawerOpen}
        onClose={() => setEvidenceDrawerOpen(false)}
        evidence={selectedEvidence}
      />
    </div>
  );
}

export default RiskIntelligence;
