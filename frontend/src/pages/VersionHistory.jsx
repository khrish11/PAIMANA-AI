import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

function VersionHistory() {
  const { id } = useParams();
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedVersion, setSelectedVersion] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        // TODO: Call actual history API
        // For now, mock data
        const mockHistory = [
          {
            version: 3,
            project_id: id,
            reporting_month: '2026-03',
            changed_by: 'admin',
            changed_at: '2026-03-15T10:30:00',
            changes: {
              revised_cost: ('110.0', '115.0'),
              expenditure: ('50.0', '55.0'),
              physical_progress: ('45.0', '50.0'),
            },
            reason: 'Monthly CUF submission for March 2026',
          },
          {
            version: 2,
            project_id: id,
            reporting_month: '2026-02',
            changed_by: 'admin',
            changed_at: '2026-02-15T10:30:00',
            changes: {
              revised_cost: ('100.0', '110.0'),
              expenditure: ('40.0', '50.0'),
              physical_progress: ('35.0', '45.0'),
            },
            reason: 'Monthly CUF submission for February 2026',
          },
          {
            version: 1,
            project_id: id,
            reporting_month: null,
            changed_by: 'admin',
            changed_at: '2026-01-01T09:00:00',
            changes: {},
            reason: 'Initial project creation',
          },
        ];
        setHistory(mockHistory);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id]);

  if (loading) return <div className="p-6">Loading version history...</div>;
  if (error) return <div className="p-6 text-red-600">Error: {error}</div>;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Version History</h1>
        <p className="text-gray-600 mt-2">Project ID: {id}</p>
      </div>

      {/* Version Timeline */}
      <div className="bg-white shadow rounded-lg border overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reporting Month</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Changed By</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Changed At</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Changes</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reason</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {history.map((version) => (
              <tr key={version.version} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm font-medium">
                    v{version.version}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {version.reporting_month || 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {version.changed_by}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(version.changed_at).toLocaleString()}
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  {Object.keys(version.changes).length > 0 ? (
                    <div className="space-y-1">
                      {Object.entries(version.changes).map(([field, values]) => (
                        <div key={field} className="text-xs">
                          <span className="font-medium">{field}:</span>
                          <span className="text-red-600 line-through mr-1">{values[0]}</span>
                          <span className="text-green-600">{values[1]}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <span className="text-gray-400">No changes</span>
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {version.reason}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    onClick={() => setSelectedVersion(version)}
                    className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 text-xs"
                  >
                    View Snapshot
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Version Snapshot Modal */}
      {selectedVersion && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Version {selectedVersion.version} Snapshot
              </h3>
              <button
                onClick={() => setSelectedVersion(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded">
                <h4 className="font-medium mb-2">Metadata</h4>
                <p><strong>Project ID:</strong> {selectedVersion.project_id}</p>
                <p><strong>Reporting Month:</strong> {selectedVersion.reporting_month || 'N/A'}</p>
                <p><strong>Changed By:</strong> {selectedVersion.changed_by}</p>
                <p><strong>Changed At:</strong> {new Date(selectedVersion.changed_at).toLocaleString()}</p>
                <p><strong>Reason:</strong> {selectedVersion.reason}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <h4 className="font-medium mb-2">Changes</h4>
                {Object.keys(selectedVersion.changes).length > 0 ? (
                  <table className="min-w-full">
                    <thead>
                      <tr className="text-left text-xs font-medium text-gray-500 uppercase">
                        <th className="pb-2">Field</th>
                        <th className="pb-2">Old Value</th>
                        <th className="pb-2">New Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(selectedVersion.changes).map(([field, values]) => (
                        <tr key={field} className="border-t">
                          <td className="py-2 font-medium">{field}</td>
                          <td className="py-2 text-red-600">{values[0]}</td>
                          <td className="py-2 text-green-600">{values[1]}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p className="text-gray-400">No changes recorded</p>
                )}
              </div>
            </div>
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedVersion(null)}
                className="px-4 py-2 border rounded-md hover:bg-gray-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default VersionHistory;
