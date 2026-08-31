import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

function ProjectReport() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch(`/api/v1/reports/project/${id}?reporting_period=2026-03`);
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
  }, [id]);

  if (loading) return <div className="p-6">Loading project report...</div>;
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
        <h1 className="text-3xl font-bold text-gray-900">Project Risk Report</h1>
        <p className="text-gray-600 mt-2">Project ID: {id}</p>
      </div>

      {/* Report Metadata */}
      <div className="bg-gray-50 border rounded-lg p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div><strong>Report ID:</strong> {data.metadata.report_id}</div>
          <div><strong>Generated At:</strong> {new Date(data.metadata.generated_at).toLocaleString()}</div>
          <div><strong>Data Source:</strong> {data.metadata.data_source.toUpperCase()}</div>
          <div><strong>Model:</strong> {data.ml?.model} ({data.ml?.version})</div>
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

      {/* Project Profile */}
      <div className="bg-white shadow rounded-lg p-6 border mb-8">
        <h3 className="text-lg font-semibold mb-4">Project Profile</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div><strong>Project ID:</strong> {data.project_profile.project_id}</div>
          <div><strong>Project Name:</strong> {data.project_profile.project_name}</div>
          <div><strong>Ministry:</strong> {data.project_profile.ministry}</div>
          <div><strong>Sector:</strong> {data.project_profile.sector}</div>
          <div><strong>State:</strong> {data.project_profile.state}</div>
          <div><strong>Status:</strong> {data.project_profile.status}</div>
          <div><strong>Sanctioned Cost:</strong> ₹{data.project_profile.sanctioned_cost?.toFixed(0)} Cr</div>
          <div><strong>Revised Cost:</strong> ₹{data.project_profile.revised_cost?.toFixed(0) || 'N/A'} Cr</div>
        </div>
      </div>

      {/* Risk Analysis */}
      <div className="bg-white shadow rounded-lg p-6 border mb-8">
        <h3 className="text-lg font-semibold mb-4">Risk Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-600">Composite Risk Score</div>
            <div className="text-2xl font-bold text-gray-900">{data.risk.composite_score.toFixed(1)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Cost Risk</div>
            <div className="text-2xl font-bold text-gray-900">{data.risk.cost_risk.toFixed(1)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Schedule Risk</div>
            <div className="text-2xl font-bold text-gray-900">{data.risk.schedule_risk.toFixed(1)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Risk Category</div>
            <div className="text-2xl font-bold text-gray-900">{data.risk.risk_category}</div>
          </div>
        </div>
      </div>

      {/* ML Prediction */}
      {data.ml && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
          <h3 className="text-lg font-semibold mb-4 text-yellow-800">ML Model Prediction</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-sm text-gray-600">Model</div>
              <div className="text-lg font-bold">{data.ml.model}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Version</div>
              <div className="text-lg font-bold">{data.ml.version}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Status</div>
              <div className="text-lg font-bold text-yellow-600">{data.ml.status.toUpperCase()}</div>
            </div>
          </div>
          <div className="mt-4 text-sm text-yellow-800">
            <strong>Warning:</strong> This model is experimental and not production validated.
          </div>
        </div>
      )}

      {/* RCF Analysis */}
      {data.rcf && (
        <div className="bg-white shadow rounded-lg p-6 border mb-8">
          <h3 className="text-lg font-semibold mb-4">Reference Class Forecasting</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-sm text-gray-600">Reference Class</div>
              <div className="text-lg font-bold">{data.rcf.reference_class}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Sample Count</div>
              <div className="text-lg font-bold">{data.rcf.sample_count}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Fallback Used</div>
              <div className="text-lg font-bold">{data.rcf.fallback_used ? 'Yes' : 'No'}</div>
            </div>
          </div>
        </div>
      )}

      {/* Anomalies */}
      <div className="bg-white shadow rounded-lg p-6 border mb-8">
        <h3 className="text-lg font-semibold mb-4">Detected Anomalies ({data.anomalies.length})</h3>
        {data.anomalies.length > 0 ? (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Observed</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Expected</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Explanation</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.anomalies.map((anomaly, idx) => (
                <tr key={idx}>
                  <td className="px-4 py-2 text-sm text-gray-900">{anomaly.type}</td>
                  <td className="px-4 py-2 text-sm">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      anomaly.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                      anomaly.severity === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {anomaly.severity}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-900">{anomaly.observed}</td>
                  <td className="px-4 py-2 text-sm text-gray-500">{anomaly.expected}</td>
                  <td className="px-4 py-2 text-sm text-gray-600">{anomaly.explanation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-gray-500">No anomalies detected</p>
        )}
      </div>

      {/* Governance Status */}
      <div className="bg-white shadow rounded-lg p-6 border">
        <h3 className="text-lg font-semibold mb-4">Governance Status</h3>
        <div>
          <div className="text-sm text-gray-600">Current Status</div>
          <div className={`text-xl font-bold ${
            data.governance.current_status === 'pending_review' ? 'text-orange-600' : 'text-green-600'
          }`}>
            {data.governance.current_status.toUpperCase()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProjectReport;
