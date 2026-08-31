import { useEffect, useState } from 'react';
import { getDashboard } from '../services/api';
import { Card, Badge, LoadingState, EmptyState } from "../components/common";
import { KPICard } from "../components/domain";
import { spacing } from '../tokens';

function NationalRiskMap() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await getDashboard();
        setData(response);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <LoadingState message="Loading dashboard..." />;
  if (error) return <EmptyState icon="⚠️" title="Error" description={error} />;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {/* Data Source Badge */}
      <div>
        <Badge variant="success">REAL PAIMANA DATA</Badge>
      </div>

      {/* ML Status Badge */}
      <div>
        <Badge variant="warning">ML STATUS: EXPERIMENTAL</Badge>
      </div>

      {/* Top Row: 6 KPI Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(6, 1fr)', 
        gap: spacing.md 
      }}>
        <KPICard
          label="Total Projects"
          value={data.kpi?.total_projects || 'N/A'}
          icon="🏗️"
        />
        <KPICard
          label="High Risk"
          value={data.kpi?.high_risk_projects || 'N/A'}
          icon="⚠️"
          trendDirection="up"
        />
        <KPICard
          label="Critical"
          value={data.kpi?.critical_projects || 'N/A'}
          icon="🚨"
          trendDirection="up"
        />
        <KPICard
          label="Average Risk"
          value={data.kpi?.average_risk?.toFixed(1) || 'N/A'}
          icon="📊"
        />
        <KPICard
          label="Average DCS"
          value={data.kpi?.average_dcs?.toFixed(1) || 'N/A'}
          icon="💚"
        />
        <KPICard
          label="Open Reviews"
          value={data.kpi?.review_queue_count || 'N/A'}
          icon="📋"
        />
      </div>

      {/* Main Row: Map + Portfolio Summary */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: spacing.lg 
      }}>
        <Card padding="lg">
          <h3 style={{ marginBottom: spacing.md }}>India Geographic Risk Map</h3>
          <div style={{ 
            height: '400px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            color: '#64748b'
          }}>
            Map visualization placeholder
          </div>
        </Card>
        <Card padding="lg">
          <h3 style={{ marginBottom: spacing.md }}>Portfolio Risk Summary</h3>
          <div style={{ 
            height: '400px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            color: '#64748b'
          }}>
            Risk summary chart placeholder
          </div>
        </Card>
      </div>

      {/* Next Row: Sector Risk + Risk Trend */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: spacing.lg 
      }}>
        <Card padding="lg">
          <h3 style={{ marginBottom: spacing.md }}>Sector Risk Distribution</h3>
          <div style={{ 
            height: '300px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            color: '#64748b'
          }}>
            Sector risk chart placeholder
          </div>
        </Card>
        <Card padding="lg">
          <h3 style={{ marginBottom: spacing.md }}>Risk Trend Over Time</h3>
          <div style={{ 
            height: '300px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            color: '#64748b'
          }}>
            Risk trend chart placeholder
          </div>
        </Card>
      </div>

      {/* Bottom Row: Top Risk Projects + Recent Alerts */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: spacing.lg 
      }}>
        {/* Top Risk Projects */}
        <Card padding="lg">
          <h3 style={{ marginBottom: spacing.md }}>Top Risk Projects</h3>
          {data.top_risk_projects && data.top_risk_projects.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
              {data.top_risk_projects.slice(0, 5).map((project, index) => (
                <div
                  key={index}
                  style={{
                    padding: spacing.md,
                    backgroundColor: '#1e293b',
                    borderRadius: '0.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                      {project.project_name}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>
                      {project.sector} - {project.state}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.125rem', fontWeight: 700, color: '#ef4444' }}>
                      {project.risk_score?.toFixed(1)}
                    </div>
                    <Badge 
                      variant={
                        project.risk_category === 'CRITICAL' ? 'critical' :
                        project.risk_category === 'VERY_HIGH' ? 'danger' :
                        project.risk_category === 'HIGH' ? 'warning' : 'success'
                      }
                      size="sm"
                    >
                      {project.risk_category}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon="📭" title="No projects" description="No risk projects found" />
          )}
        </Card>

        {/* Recent Alerts */}
        <Card padding="lg">
          <h3 style={{ marginBottom: spacing.md }}>Recent Alerts</h3>
          {data.alerts && data.alerts.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
              {data.alerts.slice(0, 5).map((alert, index) => (
                <div
                  key={index}
                  style={{
                    padding: spacing.md,
                    backgroundColor: '#1e293b',
                    borderLeft: '4px solid #ef4444',
                    borderRadius: '0.5rem',
                  }}
                >
                  <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                    {alert.title}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>
                    {alert.message}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon="📭" title="No alerts" description="No recent alerts" />
          )}
        </Card>
      </div>
    </div>
  );
}

export default NationalRiskMap;
