import { useEffect, useState } from 'react';
import { Card, LoadingState, EmptyState } from '../components/common';
import { KPICard } from '../components/domain';
import { colors, spacing, borderRadius } from '../tokens';

function DataHealth() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/api/v1/data-health');
        if (!response.ok) throw new Error('Failed to fetch data health');
        const data = await response.json();
        setData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <LoadingState message="Loading data health..." />;
  if (error) return <EmptyState icon="⚠️" title="Error" description={error} />;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {/* Primary Metrics */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(4, 1fr)', 
        gap: spacing.md 
      }}>
        <KPICard
          label="Total Records"
          value={data.metrics.total_records}
          icon="📊"
        />
        <KPICard
          label="Valid Records"
          value={data.metrics.valid_records}
          icon="✅"
          trendDirection="up"
        />
        <KPICard
          label="Warning Records"
          value={data.metrics.warning_records}
          icon="⚠️"
          trendDirection="up"
        />
        <KPICard
          label="Excluded Records"
          value={data.metrics.excluded_records}
          icon="🚫"
          trendDirection="up"
        />
      </div>

      {/* Secondary Metrics */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)', 
        gap: spacing.md 
      }}>
        <KPICard
          label="Duplicate Count"
          value={data.metrics.duplicate_count}
          icon="🔁"
          trendDirection="up"
        />
        <KPICard
          label="Unresolved Conflicts"
          value={data.metrics.unresolved_conflicts}
          icon="⚔️"
          trendDirection="up"
        />
        <KPICard
          label="Missing Critical Fields"
          value={data.metrics.missing_critical_fields}
          icon="❓"
          trendDirection="up"
        />
      </div>

      {/* Tertiary Metrics */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)', 
        gap: spacing.md 
      }}>
        <KPICard
          label="Stale Projects"
          value={data.metrics.stale_projects}
          icon="🕰️"
          trendDirection="up"
        />
        <KPICard
          label="Low-DCS Projects"
          value={data.metrics.low_dcs_projects}
          icon="📉"
          trendDirection="up"
        />
        <KPICard
          label="Anomalies Detected"
          value={data.metrics.anomaly_count}
          icon="🔍"
          trendDirection="up"
        />
      </div>

      {/* Charts */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: spacing.lg 
      }}>
        <Card padding="lg">
          <h3 style={{ marginBottom: spacing.md }}>Data Quality Trend</h3>
          <div style={{ 
            height: '256px', 
            backgroundColor: colors.background.tertiary,
            borderRadius: borderRadius.md,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: colors.text.muted 
          }}>
            Chart: DCS Score Over Time
          </div>
        </Card>
        <Card padding="lg">
          <h3 style={{ marginBottom: spacing.md }}>Missingness by Field</h3>
          <div style={{ 
            height: '256px', 
            backgroundColor: colors.background.tertiary,
            borderRadius: borderRadius.md,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: colors.text.muted 
          }}>
            Chart: Missing Data Percentage
          </div>
        </Card>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: spacing.lg 
      }}>
        <Card padding="lg">
          <h3 style={{ marginBottom: spacing.md }}>Issues by Month</h3>
          <div style={{ 
            height: '256px', 
            backgroundColor: colors.background.tertiary,
            borderRadius: borderRadius.md,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: colors.text.muted 
          }}>
            Chart: Issues per Month
          </div>
        </Card>
        <Card padding="lg">
          <h3 style={{ marginBottom: spacing.md }}>Issues by Sector</h3>
          <div style={{ 
            height: '256px', 
            backgroundColor: colors.background.tertiary,
            borderRadius: borderRadius.md,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: colors.text.muted 
          }}>
            Chart: Issues per Sector
          </div>
        </Card>
      </div>

      {/* Issues by State */}
      <Card padding="lg">
        <h3 style={{ marginBottom: spacing.md }}>Issues by State</h3>
        <div style={{ 
          height: '256px', 
          backgroundColor: colors.background.tertiary,
          borderRadius: borderRadius.md,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: colors.text.muted 
        }}>
          Chart: Issues per State
        </div>
      </Card>
    </div>
  );
}

export default DataHealth;
