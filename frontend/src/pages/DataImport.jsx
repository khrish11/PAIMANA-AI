import { useState } from 'react';

function DataImport() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);
  const [showPreview, setShowPreview] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && (selectedFile.name.endsWith('.csv') || selectedFile.name.endsWith('.xlsx') || selectedFile.name.endsWith('.xls'))) {
      setFile(selectedFile);
      setPreview(null);
      setResult(null);
      setShowPreview(false);
    } else {
      alert('Please select a CSV or XLSX file');
    }
  };

  const handlePreview = async () => {
    if (!file) return;

    setImporting(true);
    // TODO: Call preview API
    // Mock preview for now
    setTimeout(() => {
      setPreview({
        total_rows: 100,
        valid_rows: 85,
        warning_rows: 10,
        rejected_rows: 5,
        duplicate_rows: 0,
        errors: [
          { row: 3, field: 'sanctioned_cost', message: 'sanctioned_cost must be positive' },
          { row: 7, field: 'project_id', message: 'Missing required field: project_id' },
          { row: 15, field: 'physical_progress', message: 'physical_progress must be between 0 and 100' },
          { row: 22, field: 'sanctioned_cost', message: 'sanctioned_cost must be a valid number' },
          { row: 45, field: 'project_id', message: 'Missing required field: project_id' },
        ],
        warnings: [
          { row: 2, warnings: ['Missing revised_cost', 'Missing expenditure'] },
          { row: 8, warnings: ['Missing physical_progress'] },
          { row: 12, warnings: ['Missing revised_cost'] },
          { row: 18, warnings: ['Missing expenditure', 'Missing physical_progress'] },
          { row: 25, warnings: ['Missing revised_cost'] },
          { row: 30, warnings: ['Missing expenditure'] },
          { row: 35, warnings: ['Missing physical_progress'] },
          { row: 40, warnings: ['Missing revised_cost', 'Missing expenditure'] },
          { row: 50, warnings: ['Missing physical_progress'] },
          { row: 55, warnings: ['Missing revised_cost'] },
        ],
      });
      setShowPreview(true);
      setImporting(false);
    }, 1000);
  };

  const handleImport = async () => {
    if (!file || !preview) return;

    setImporting(true);
    // TODO: Call import API
    // Mock import for now
    setTimeout(() => {
      setResult({
        import_id: 'imp-' + Date.now(),
        filename: file.name,
        user: 'admin',
        timestamp: new Date().toISOString(),
        successful_rows: preview.valid_rows,
        warning_rows: preview.warning_rows,
        rejected_rows: preview.rejected_rows,
      });
      setImporting(false);
    }, 2000);
  };

  const downloadErrorReport = () => {
    // TODO: Generate and download error report
    console.log('Downloading error report...');
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setShowPreview(false);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Data Import</h1>
        <p className="text-gray-600 mt-2">Import project data from CSV or XLSX files</p>
      </div>

      {!result ? (
        <>
          {/* File Upload */}
          <div className="bg-white shadow rounded-lg p-6 border mb-6">
            <h2 className="text-xl font-semibold mb-4">Upload File</h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Select File
              </label>
              <p className="mt-2 text-sm text-gray-500">
                Supported formats: CSV, XLSX, XLS
              </p>
              {file && (
                <p className="mt-2 text-sm text-green-600 font-medium">
                  Selected: {file.name}
                </p>
              )}
            </div>
            {file && (
              <div className="mt-4 flex space-x-4">
                <button
                  onClick={handlePreview}
                  disabled={importing}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {importing ? 'Previewing...' : 'Preview'}
                </button>
                <button
                  onClick={reset}
                  className="px-6 py-2 border rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>

          {/* Preview */}
          {showPreview && preview && (
            <div className="bg-white shadow rounded-lg p-6 border mb-6">
              <h2 className="text-xl font-semibold mb-4">Import Preview</h2>
              
              {/* Summary */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Total Rows</div>
                  <div className="text-2xl font-bold text-blue-600">{preview.total_rows}</div>
                </div>
                <div className="bg-green-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Valid Rows</div>
                  <div className="text-2xl font-bold text-green-600">{preview.valid_rows}</div>
                </div>
                <div className="bg-yellow-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Warning Rows</div>
                  <div className="text-2xl font-bold text-yellow-600">{preview.warning_rows}</div>
                </div>
                <div className="bg-red-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Rejected Rows</div>
                  <div className="text-2xl font-bold text-red-600">{preview.rejected_rows}</div>
                </div>
              </div>

              {/* Errors */}
              {preview.errors.length > 0 && (
                <div className="mb-6">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-semibold text-red-600">Errors ({preview.errors.length})</h3>
                    <button
                      onClick={downloadErrorReport}
                      className="text-sm text-blue-600 hover:underline"
                    >
                      Download Error Report
                    </button>
                  </div>
                  <div className="bg-red-50 border border-red-200 rounded max-h-48 overflow-y-auto">
                    <table className="min-w-full">
                      <thead className="bg-red-100">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-red-800">Row</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-red-800">Field</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-red-800">Message</th>
                        </tr>
                      </thead>
                      <tbody>
                        {preview.errors.map((error, idx) => (
                          <tr key={idx} className="border-t border-red-200">
                            <td className="px-4 py-2 text-sm">{error.row}</td>
                            <td className="px-4 py-2 text-sm">{error.field}</td>
                            <td className="px-4 py-2 text-sm">{error.message}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Warnings */}
              {preview.warnings.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-yellow-600 mb-2">Warnings ({preview.warnings.length})</h3>
                  <div className="bg-yellow-50 border border-yellow-200 rounded max-h-48 overflow-y-auto">
                    <table className="min-w-full">
                      <thead className="bg-yellow-100">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-yellow-800">Row</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-yellow-800">Warnings</th>
                        </tr>
                      </thead>
                      <tbody>
                        {preview.warnings.slice(0, 10).map((warning, idx) => (
                          <tr key={idx} className="border-t border-yellow-200">
                            <td className="px-4 py-2 text-sm">{warning.row}</td>
                            <td className="px-4 py-2 text-sm">{warning.warnings.join(', ')}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex space-x-4">
                <button
                  onClick={handleImport}
                  disabled={importing || preview.valid_rows === 0}
                  className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400"
                >
                  {importing ? 'Importing...' : `Import ${preview.valid_rows} Valid Rows`}
                </button>
                <button
                  onClick={reset}
                  className="px-6 py-2 border rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </>
      ) : (
        /* Import Result */
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h1 className="text-2xl font-bold text-green-800 mb-4">Import Successful</h1>
          <div className="space-y-2">
            <p><strong>Import ID:</strong> {result.import_id}</p>
            <p><strong>Filename:</strong> {result.filename}</p>
            <p><strong>User:</strong> {result.user}</p>
            <p><strong>Timestamp:</strong> {new Date(result.timestamp).toLocaleString()}</p>
            <p><strong>Successful Rows:</strong> {result.successful_rows}</p>
            <p><strong>Warning Rows:</strong> {result.warning_rows}</p>
            <p><strong>Rejected Rows:</strong> {result.rejected_rows}</p>
          </div>
          <div className="mt-6 flex space-x-4">
            <button
              onClick={reset}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Import Another File
            </button>
            <button
              onClick={() => window.location.href = '/data-management'}
              className="px-6 py-2 border rounded-md hover:bg-gray-50"
            >
              View Imported Data
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DataImport;
