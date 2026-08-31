import { useEffect, useState } from 'react';

function NationalReport() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters] = useState({
    reporting_period: '2026-03',
  });

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch(`/api/v1/reports/national?reporting_period=${filters.reporting_period}`);
        if (!response.ok) throw new Error('Failed to fetch report');
        const data = await response.json();
        setData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [filters]);

  if (loading) return <div className="p-6">Loading national report...</div>;
  if (error) return <div className="p-6 text-red-600">Error: {error}</div>;

  const handleExportPDF = () => {
    console.log('Exporting to PDF...');
  };

  const handleExportCSV = () => {
    console.log('Exporting to CSV...');
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">National Risk Report</h1>
        <p className="text-gray-600 mt-2">National-level infrastructure risk overview</p>
      </div>

      {/* Report Metadata */}
      <div className="bg-gray-50 border rounded-lg p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div><strong>Report ID:</strong> {data.metadata.report_id}</div>
          <div><strong>Generated At:</strong> {new Date(data.metadata.generated_at).toLocaleString()}</div>
          <div><strong>Reporting Period:</strong> {data.metadata.reporting_period}</div>
          <div><strong>Data Source:</strong> {data.metadata.data_source.toUpperCase()}</div>
          <div><strong>Model Version:</strong> {data.metadata.model_version}</div>
          <div><strong>Data Snapshot:</strong> {new Date(data.metadata.data_snapshot_timestamp).toLocaleString()}</div>
        </div>
      </div>

      {/* Export Buttons */}
      <div className="flex space-x-4 mb-6">
        <button onClick={handleExportPDF} className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
          Export PDF
        </button>
        <button onClick={handleExportCSV} className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
          Export CSV
        </button>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white shadow rounded-lg p-6 border">
          <div className="text-sm text-gray-600">Total Projects</div>
          <div className="text-3xl font-bold text-gray-900">{data.total_projects}</div>
        </div>
        <div className="bg-white shadow rounded-lg p-6 border">
          <div className="text-sm text-gray-600">Average Risk</div>
          <div className="text-3xl font-bold text-gray-900">{data.average_risk.toFixed(1)}</div>
        </div>
        <div className="bg-white shadow rounded-lg p-6 border">
          <div className="text-sm text-gray-600">Average DCS</div>
          <div className="text-3xl font-bold text-gray-900">{data.average_dcs.toFixed(1)}</div>
        </div>
        <div className="bg-white shadow rounded-lg p-6 border">
          <div className="text-sm text-gray-600">Anomalies</div>
          <div className="text-3xl font-bold text-purple-600">{data.anomaly_count}</div>
        </div>
      </div>

      {/* Risk Distribution */}
      <div className="bg-white shadow rounded-lg p-6 border mb-8">
        <h3 className="text-lg font-semibold mb-4">Risk Distribution</h3>
        <div className="grid grid-cols-5 gap-4">
          <div className="bg-green-50 p-4 rounded text-center">
            <div className="text-2xl font-bold text-green-600">{data.risk_distribution.LOW}</div>
            <div className="text-sm text-gray-600">Low</div>
          </div>
          <div className="bg-blue-50 p-4 rounded text-center">
            <div className="text-2xl font-bold text-blue-600">{data.risk_distribution.MODERATE}</div>
            <div className="text-sm text-gray-600">Moderate</div>
          </div>
          <div className="bg-yellow-50 p-4 rounded text-center">
            <div className="text-2xl font-bold text-yellow-600">{data.risk_distribution.HIGH}</div>
            <div className="text-sm text-gray-600">High</div>
          </div>
          <div className="bg-orange-50 p-4 rounded text-center">
            <div className="text-2xl font-bold text-orange-600">{data.risk_distribution.VERY_HIGH}</div>
            <div className="text-sm text-gray-600">Very High</div>
          </div>
          <div className="bg-red-50 p-4 rounded text-center">
            <div className="text-2xl font-bold text-red-600">{data.risk_distribution.CRITICAL}</div>
            <div className="text-sm text-gray-600">Critical</div>
          </div>
        </div>
      </div>

      {/* State-Level Risk */}
      <div className="bg-white shadow rounded-lg p-6 border mb-8">
        <h3 className="text-lg font-semibold mb-4">State-Level Risk</h3>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">State</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Projects</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Avg Risk</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {Object.entries(data.state_level_risk).map(([state, metrics]) => (
              <tr key={state}>
                <td className="px-4 py-2 text-sm text-gray-900">{state}</td>
                <td className="px-4 py-2 text-sm text-gray-500">{metrics.project_count}</td>
                <td className="px-4 py-2 text-sm text-gray-900">{metrics.average_risk.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Sector-Level Risk */}
      <div className="bg-white shadow rounded-lg p-6 border mb-8">
        <h3 className="text-lg font-semibold mb-4">Sector-Level Risk</h3>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Sector</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Projects</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Avg Risk</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {Object.entries(data.sector_level_risk).map(([sector, metrics]) => (
              <tr key={sector}>
                <td className="px-4 py-2 text-sm text-gray-900">{sector}</td>
                <td className="px-4 py-2 text-sm text-gray-500">{metrics.project_count}</td>
                <td className="px-4 py-2 text-sm text-gray-900">{metrics.average_risk.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Governance Queue Stats */}
      <div className="bg-white shadow rounded-lg p-6 border">
        <h3 className="text-lg font-semibold mb-4">Governance Queue Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-600">Total Reviews</div>
            <div className="text-xl font-bold text-gray-900">{data.governance_queue_stats.total_reviews}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Open Reviews</div>
            <div className="text-xl font-bold text-orange-600">{data.governance_queue_stats.open_reviews}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Overdue Reviews</div>
            <div className="text-xl font-bold text-red-600">{data.governance_queue_stats.overdue_reviews}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Model Status</div>
            <div className="text-xl font-bold text-yellow-600">{data.model_status}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default NationalReport;
