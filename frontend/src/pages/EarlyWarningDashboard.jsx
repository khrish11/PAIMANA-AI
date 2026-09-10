import { useEffect, useState } from 'react';
import { Card, Badge, Button, LoadingState, EmptyState } from '../components/common';
import { colors, spacing, typography, borderRadius } from '../tokens';

function EarlyWarningDashboard() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: 'OPEN',
    severity: null,
    ministry: null,
    sector: null,
  });
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchAlerts();
    fetchStats();
  }, [filters]);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.severity) params.append('severity', filters.severity);
      if (filters.ministry) params.append('ministry', filters.ministry);
      if (filters.sector) params.append('sector', filters.sector);
      
      const response = await fetch(`http://localhost:8001/api/v1/alerts?${params}`);
      if (!response.ok) throw new Error('Failed to fetch alerts');
      const data = await response.json();
      setAlerts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/v1/alerts/stats/summary');
      if (!response.ok) throw new Error('Failed to fetch stats');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const handleAcknowledge = async (alertId) => {
    try {
      const response = await fetch(`http://localhost:8001/api/v1/alerts/${alertId}/acknowledge`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to acknowledge alert');
      fetchAlerts();
      fetchStats();
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  const handleResolve = async (alertId) => {
    try {
      const response = await fetch(`http://localhost:8001/api/v1/alerts/${alertId}/resolve`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to resolve alert');
      fetchAlerts();
      fetchStats();
    } catch (err) {
      console.error('Failed to resolve alert:', err);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return colors.accent.danger;
      case 'HIGH': return colors.accent.warning;
      case 'MODERATE': return colors.accent.info;
      case 'LOW': return colors.accent.success;
      default: return colors.text.secondary;
    }
  };

  const getAlertTypeLabel = (type) => {
    const labels = {
      ml_cost_risk: 'ML Cost Risk',
      ml_schedule_risk: 'ML Schedule Risk',
      hybrid_risk: 'Hybrid Risk',
      progress_deterioration: 'Progress Deterioration',
      expenditure_progress_mismatch: 'Expenditure-Progress Mismatch',
      milestone_slippage: 'Milestone Slippage',
      cost_escalation_trend: 'Cost Escalation Trend',
      negative_monthly_change: 'Negative Monthly Change',
      anomaly_signal: 'Anomaly Signal',
      positive_deviance_signal: 'Positive Deviance',
      dcs_low: 'Low Data Confidence',
    };
    return labels[type] || type;
  };

  if (loading) return <LoadingState message="Loading early warning alerts..." />;
  if (error) return (
    <EmptyState 
      icon="⚠️" 
      title="Alerts Unavailable" 
      description="We couldn't retrieve the early warning alerts."
    >
      <Button variant="primary" onClick={fetchAlerts}>Retry</Button>
    </EmptyState>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: typography.fontSize['2xl'], fontWeight: 600, color: colors.text.primary, marginBottom: spacing.xs }}>
            Early Warning Dashboard
          </h1>
          <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
            Proactive alerts based on ML predictions and rule-based signals
          </p>
        </div>
        <Button variant="secondary" onClick={fetchAlerts}>Refresh</Button>
      </div>

      {/* Statistics */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: spacing.lg }}>
          <Card padding="md">
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Total Open
            </div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 600, color: colors.text.primary }}>
              {stats.total_open}
            </div>
          </Card>
          <Card padding="md">
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Critical
            </div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 600, color: colors.accent.danger }}>
              {stats.by_severity.CRITICAL}
            </div>
          </Card>
          <Card padding="md">
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              High
            </div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 600, color: colors.accent.warning }}>
              {stats.by_severity.HIGH}
            </div>
          </Card>
          <Card padding="md">
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Moderate
            </div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 600, color: colors.accent.info }}>
              {stats.by_severity.MODERATE}
            </div>
          </Card>
          <Card padding="md">
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
              Low
            </div>
            <div style={{ fontSize: typography.fontSize['2xl'], fontWeight: 600, color: colors.accent.success }}>
              {stats.by_severity.LOW}
            </div>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card padding="md">
        <div style={{ display: 'flex', gap: spacing.md, alignItems: 'center' }}>
          <div>
            <label style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs, display: 'block' }}>
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              style={{
                padding: `${spacing.xs} ${spacing.sm}`,
                borderRadius: borderRadius.sm,
                border: `1px solid ${colors.border.default}`,
                fontSize: typography.fontSize.base,
              }}
            >
              <option value="OPEN">Open</option>
              <option value="ACKNOWLEDGED">Acknowledged</option>
              <option value="RESOLVED">Resolved</option>
              <option value="">All</option>
            </select>
          </div>
          <div>
            <label style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs, display: 'block' }}>
              Severity
            </label>
            <select
              value={filters.severity || ''}
              onChange={(e) => setFilters({ ...filters, severity: e.target.value || null })}
              style={{
                padding: `${spacing.xs} ${spacing.sm}`,
                borderRadius: borderRadius.sm,
                border: `1px solid ${colors.border.default}`,
                fontSize: typography.fontSize.base,
              }}
            >
              <option value="">All</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MODERATE">Moderate</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Alerts List */}
      {alerts.length === 0 ? (
        <Card padding="lg">
          <EmptyState icon="✓" title="No Alerts" description="No alerts match the current filters." />
        </Card>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
          {alerts.map((alert) => (
            <Card key={alert.alert_id} padding="lg">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: spacing.md }}>
                <div style={{ display: 'flex', gap: spacing.sm, alignItems: 'center' }}>
                  <Badge variant={alert.severity.toLowerCase()} size="md">
                    {alert.severity}
                  </Badge>
                  <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: colors.text.primary }}>
                    {getAlertTypeLabel(alert.alert_type)}
                  </div>
                </div>
                <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
                  {new Date(alert.created_at).toLocaleString()}
                </div>
              </div>
              
              <div style={{ marginBottom: spacing.md }}>
                <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                  Trigger
                </div>
                <div style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
                  {alert.trigger}
                </div>
              </div>

              {alert.evidence && (
                <div style={{ marginBottom: spacing.md }}>
                  <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted, marginBottom: spacing.xs }}>
                    Evidence
                  </div>
                  <div style={{ 
                    padding: spacing.md, 
                    backgroundColor: colors.background.tertiary, 
                    borderRadius: borderRadius.sm,
                    fontSize: typography.fontSize.sm,
                    color: colors.text.secondary,
                    whiteSpace: 'pre-wrap',
                  }}>
                    {JSON.stringify(alert.evidence, null, 2)}
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', gap: spacing.sm, justifyContent: 'flex-end' }}>
                {alert.status === 'OPEN' && (
                  <>
                    <Button variant="secondary" size="sm" onClick={() => handleAcknowledge(alert.alert_id)}>
                      Acknowledge
                    </Button>
                    <Button variant="primary" size="sm" onClick={() => handleResolve(alert.alert_id)}>
                      Resolve
                    </Button>
                  </>
                )}
                {alert.status === 'ACKNOWLEDGED' && (
                  <Button variant="primary" size="sm" onClick={() => handleResolve(alert.alert_id)}>
                    Resolve
                  </Button>
                )}
                <Badge variant={alert.status === 'OPEN' ? 'danger' : alert.status === 'ACKNOWLEDGED' ? 'warning' : 'success'} size="sm">
                  {alert.status}
                </Badge>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

export default EarlyWarningDashboard;
