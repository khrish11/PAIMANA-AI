import { useEffect, useState } from 'react';

function GovernanceReport() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/api/v1/reports/governance?reporting_period=2026-03');
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
  }, []);

  if (loading) return <div className="p-6">Loading governance report...</div>;
  if (error) return <div className="p-6 text-red-600">Error: {error}</div>;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Governance Report</h1>
        <p className="text-gray-600 mt-2">Governance queue and review statistics</p>
      </div>

      {/* Report Metadata */}
      <div className="bg-gray-50 border rounded-lg p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div><strong>Report ID:</strong> {data.metadata.report_id}</div>
          <div><strong>Generated At:</strong> {new Date(data.metadata.generated_at).toLocaleString()}</div>
          <div><strong>Reporting Period:</strong> {data.metadata.reporting_period}</div>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white shadow rounded-lg p-6 border">
          <div className="text-sm text-gray-600">Total Reviews</div>
          <div className="text-3xl font-bold text-gray-900">{data.total_reviews}</div>
        </div>
        <div className="bg-white shadow rounded-lg p-6 border">
          <div className="text-sm text-gray-600">Open Reviews</div>
          <div className="text-3xl font-bold text-orange-600">{data.open_reviews}</div>
        </div>
        <div className="bg-white shadow rounded-lg p-6 border">
          <div className="text-sm text-gray-600">Overdue Reviews</div>
          <div className="text-3xl font-bold text-red-600">{data.overdue_reviews}</div>
        </div>
        <div className="bg-white shadow rounded-lg p-6 border">
          <div className="text-sm text-gray-600">Completed Reviews</div>
          <div className="text-3xl font-bold text-green-600">{data.completed_reviews}</div>
        </div>
      </div>

      {/* Risk Distribution in Queue */}
      <div className="bg-white shadow rounded-lg p-6 border mb-8">
        <h3 className="text-lg font-semibold mb-4">Risk Distribution in Queue</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-yellow-50 p-4 rounded text-center">
            <div className="text-2xl font-bold text-yellow-600">{data.high_risk_count}</div>
            <div className="text-sm text-gray-600">High Risk</div>
          </div>
          <div className="bg-orange-50 p-4 rounded text-center">
            <div className="text-2xl font-bold text-orange-600">{data.very_high_count}</div>
            <div className="text-sm text-gray-600">Very High Risk</div>
          </div>
          <div className="bg-red-50 p-4 rounded text-center">
            <div className="text-2xl font-bold text-red-600">{data.critical_count}</div>
            <div className="text-sm text-gray-600">Critical Risk</div>
          </div>
        </div>
      </div>

      {/* Review SLA */}
      <div className="bg-white shadow rounded-lg p-6 border mb-8">
        <h3 className="text-lg font-semibold mb-4">Review SLA Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-600">Average Days to Complete</div>
            <div className="text-xl font-bold text-gray-900">{data.review_sla.average_days}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">SLA Met Percentage</div>
            <div className="text-xl font-bold text-green-600">{data.review_sla.sla_met_pct}%</div>
          </div>
        </div>
      </div>

      {/* Actions Taken */}
      <div className="bg-white shadow rounded-lg p-6 border mb-8">
        <h3 className="text-lg font-semibold mb-4">Actions Taken</h3>
        {data.actions_taken.length > 0 ? (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Count</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.actions_taken.map((action, idx) => (
                <tr key={idx}>
                  <td className="px-4 py-2 text-sm text-gray-900">{action.action}</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{action.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-gray-500">No actions recorded yet</p>
        )}
      </div>

      {/* Outcomes */}
      <div className="bg-white shadow rounded-lg p-6 border">
        <h3 className="text-lg font-semibold mb-4">Review Outcomes</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-gray-600">Approved</div>
            <div className="text-xl font-bold text-green-600">{data.outcomes.approved}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Deferred</div>
            <div className="text-xl font-bold text-yellow-600">{data.outcomes.deferred}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Escalated</div>
            <div className="text-xl font-bold text-red-600">{data.outcomes.escalated}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GovernanceReport;
