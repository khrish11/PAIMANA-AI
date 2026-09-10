import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { previewBulkImport, executeBulkImport } from '../services/api';
import { invalidateAfterBulkImport } from '../hooks';

function DataImport() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [csvContent, setCsvContent] = useState(null);
  const [preview, setPreview] = useState(null);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [error, setError] = useState(null);
  const [allowRevisions, setAllowRevisions] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && (selectedFile.name.endsWith('.csv') || selectedFile.name.endsWith('.xlsx') || selectedFile.name.endsWith('.xls'))) {
      setFile(selectedFile);
      setPreview(null);
      setResult(null);
      setShowPreview(false);
      setError(null);
      
      // Read file content
      const reader = new FileReader();
      reader.onload = (event) => {
        setCsvContent(event.target.result);
      };
      reader.readAsText(selectedFile);
    } else {
      setError('Please select a CSV or XLSX file');
    }
  };

  const handlePreview = async () => {
    if (!file || !csvContent) return;

    setImporting(true);
    setError(null);

    try {
      const batchName = file.name.replace(/\.[^/.]+$/, '');
      const previewResult = await previewBulkImport(
        csvContent,
        batchName,
        'csv',
        file.name
      );
      setPreview(previewResult);
      setShowPreview(true);
    } catch (err) {
      setError(err.message || 'Failed to preview import');
    } finally {
      setImporting(false);
    }
  };

  const handleImport = async () => {
    if (!file || !csvContent || !preview) return;

    setImporting(true);
    setError(null);

    try {
      const batchName = file.name.replace(/\.[^/.]+$/, '');
      const importResult = await executeBulkImport(
        csvContent,
        batchName,
        'csv',
        file.name,
        allowRevisions
      );
      
      // Invalidate caches after successful bulk import
      if (importResult.status === 'completed') {
        invalidateAfterBulkImport();
      }
      
      setResult(importResult);
    } catch (err) {
      setError(err.message || 'Failed to execute import');
      setImporting(false);
    }
  };

  const downloadErrorReport = () => {
    // TODO: Generate and download error report
    console.log('Downloading error report...');
  };

  const reset = () => {
    setFile(null);
    setCsvContent(null);
    setPreview(null);
    setResult(null);
    setShowPreview(false);
    setError(null);
    setAllowRevisions(false);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Data Import</h1>
        <p className="text-gray-600 mt-2">Import project data from CSV files with validation and preview</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {!result ? (
        <>
          {/* File Upload */}
          <div className="bg-white shadow rounded-lg p-6 border mb-6">
            <h2 className="text-xl font-semibold mb-4">STEP 1: Upload File</h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Select CSV File
              </label>
              <p className="mt-2 text-sm text-gray-500">
                Supported format: CSV
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
                  {importing ? 'Validating...' : 'STEP 2: Validate & Preview'}
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
              <h2 className="text-xl font-semibold mb-4">STEP 3: Import Preview</h2>
              
              {/* Summary */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Rows Detected</div>
                  <div className="text-2xl font-bold text-blue-600">{preview.rows_detected}</div>
                </div>
                <div className="bg-green-50 p-4 rounded">
                  <div className="text-sm text-gray-600">New Projects</div>
                  <div className="text-2xl font-bold text-green-600">{preview.new_projects}</div>
                </div>
                <div className="bg-purple-50 p-4 rounded">
                  <div className="text-sm text-gray-600">New Submissions</div>
                  <div className="text-2xl font-bold text-purple-600">{preview.new_submissions}</div>
                </div>
                <div className="bg-yellow-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Existing Projects</div>
                  <div className="text-2xl font-bold text-yellow-600">{preview.existing_projects}</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-orange-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Duplicate Submissions</div>
                  <div className="text-2xl font-bold text-orange-600">{preview.duplicate_submissions}</div>
                </div>
                <div className="bg-teal-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Revisions</div>
                  <div className="text-2xl font-bold text-teal-600">{preview.revisions}</div>
                </div>
                <div className="bg-red-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Invalid Rows</div>
                  <div className="text-2xl font-bold text-red-600">{preview.invalid_rows}</div>
                </div>
                <div className="bg-gray-50 p-4 rounded">
                  <div className="text-sm text-gray-600">Missing Fields</div>
                  <div className="text-2xl font-bold text-gray-600">{preview.missing_fields}</div>
                </div>
              </div>

              {/* Errors */}
              {preview.errors && preview.errors.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-red-600 mb-2">Validation Errors ({preview.errors.length})</h3>
                  <div className="bg-red-50 border border-red-200 rounded max-h-48 overflow-y-auto">
                    <table className="min-w-full">
                      <thead className="bg-red-100">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-red-800">Error</th>
                        </tr>
                      </thead>
                      <tbody>
                        {preview.errors.slice(0, 20).map((error, idx) => (
                          <tr key={idx} className="border-t border-red-200">
                            <td className="px-4 py-2 text-sm">{error}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Preview Rows */}
              {preview.preview_rows && preview.preview_rows.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-700 mb-2">Preview Rows (First 10)</h3>
                  <div className="bg-gray-50 border rounded max-h-64 overflow-y-auto">
                    <table className="min-w-full">
                      <thead className="bg-gray-100">
                        <tr>
                          {Object.keys(preview.preview_rows[0]).map((key) => (
                            <th key={key} className="px-4 py-2 text-left text-xs font-medium text-gray-800">{key}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {preview.preview_rows.map((row, idx) => (
                          <tr key={idx} className="border-t">
                            {Object.values(row).map((val, vIdx) => (
                              <td key={vIdx} className="px-4 py-2 text-sm">{val || '-'}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Revision Option */}
              {preview.duplicate_submissions > 0 && (
                <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={allowRevisions}
                      onChange={(e) => setAllowRevisions(e.target.checked)}
                      className="rounded"
                    />
                    <span className="text-sm text-yellow-800">
                      Allow revisions for {preview.duplicate_submissions} duplicate submissions (requires revision reason)
                    </span>
                  </label>
                </div>
              )}

              {/* Actions */}
              <div className="flex space-x-4">
                <button
                  onClick={handleImport}
                  disabled={importing || preview.invalid_rows > 0}
                  className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400"
                >
                  {importing ? 'Importing...' : 'STEP 4: Confirm Import'}
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
          <h1 className="text-2xl font-bold text-green-800 mb-4">Import {result.status === 'completed' ? 'Successful' : 'Failed'}</h1>
          <div className="space-y-2">
            <p><strong>Batch ID:</strong> {result.batch_id}</p>
            <p><strong>Status:</strong> {result.status}</p>
            <p><strong>Rows Detected:</strong> {result.rows_detected}</p>
            <p><strong>New Projects:</strong> {result.new_projects}</p>
            <p><strong>Existing Projects:</strong> {result.existing_projects}</p>
            <p><strong>New Submissions:</strong> {result.new_submissions}</p>
            <p><strong>Duplicate Submissions:</strong> {result.duplicate_submissions}</p>
            <p><strong>Revisions:</strong> {result.revisions}</p>
            <p><strong>Invalid Rows:</strong> {result.invalid_rows}</p>
            {result.started_at && <p><strong>Started:</strong> {new Date(result.started_at).toLocaleString()}</p>}
            {result.completed_at && <p><strong>Completed:</strong> {new Date(result.completed_at).toLocaleString()}</p>}
            {result.error_message && <p><strong>Error:</strong> {result.error_message}</p>}
          </div>
          <div className="mt-6 flex space-x-4">
            <button
              onClick={reset}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Import Another File
            </button>
            <button
              onClick={() => navigate('/data-management')}
              className="px-6 py-2 border rounded-md hover:bg-gray-50"
            >
              View Data Management
            </button>
            <button
              onClick={() => navigate('/data-import/history')}
              className="px-6 py-2 border rounded-md hover:bg-gray-50"
            >
              View Import History
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DataImport;
