import { useEffect, useState } from 'react';

function ModelReport() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/api/v1/reports/models?reporting_period=2026-03');
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

  if (loading) return <div className="p-6">Loading model report...</div>;
  if (error) return <div className="p-6 text-red-600">Error: {error}</div>;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Model Performance Report</h1>
        <p className="text-gray-600 mt-2">Experimental ML model metrics and evaluation</p>
      </div>

      {/* Experimental Warning */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <div className="flex items-center">
          <span className="text-2xl mr-3">⚠️</span>
          <div>
            <h3 className="font-semibold text-yellow-800">{data.experimental_warning}</h3>
            <p className="text-sm text-yellow-700 mt-1">
              These models are trained on limited PAIMANA data and have not been production validated.
              Use predictions for reference only.
            </p>
          </div>
        </div>
      </div>

      {/* Report Metadata */}
      <div className="bg-gray-50 border rounded-lg p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div><strong>Report ID:</strong> {data.metadata.report_id}</div>
          <div><strong>Generated At:</strong> {new Date(data.metadata.generated_at).toLocaleString()}</div>
          <div><strong>Training Period:</strong> {data.training_period}</div>
          <div><strong>Holdout Size:</strong> {data.holdout_size} projects</div>
        </div>
      </div>

      {/* Model Metrics */}
      <div className="space-y-6">
        {data.models.map((model) => (
          <div key={model.name} className="bg-white shadow rounded-lg p-6 border">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">{model.name}</h3>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                {model.version}
              </span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 p-4 rounded">
                <div className="text-sm text-gray-600">F1 Score</div>
                <div className="text-2xl font-bold text-gray-900">{model.f1.toFixed(2)}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <div className="text-sm text-gray-600">Precision</div>
                <div className="text-2xl font-bold text-gray-900">{model.precision.toFixed(2)}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <div className="text-sm text-gray-600">Recall</div>
                <div className="text-2xl font-bold text-gray-900">{model.recall.toFixed(2)}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <div className="text-sm text-gray-600">ROC-AUC</div>
                <div className="text-2xl font-bold text-gray-900">{model.roc_auc.toFixed(2)}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <div className="text-sm text-gray-600">PR-AUC</div>
                <div className="text-2xl font-bold text-gray-900">{model.pr_auc.toFixed(2)}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <div className="text-sm text-gray-600">Brier Score</div>
                <div className="text-2xl font-bold text-gray-900">{model.brier.toFixed(2)}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <div className="text-sm text-gray-600">MCC</div>
                <div className="text-2xl font-bold text-gray-900">{model.mcc.toFixed(2)}</div>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <div className="text-sm text-gray-600">Balanced Accuracy</div>
                <div className="text-2xl font-bold text-gray-900">{model.balanced_accuracy.toFixed(2)}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* SHAP Availability */}
      <div className="mt-8 bg-white shadow rounded-lg p-6 border">
        <h3 className="text-lg font-semibold mb-4">SHAP Explanations</h3>
        <div className="flex items-center">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            data.shap_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {data.shap_available ? 'Available' : 'Not Available'}
          </span>
          <span className="ml-4 text-sm text-gray-600">
            {data.shap_available 
              ? 'SHAP explanations can be generated for model predictions' 
              : 'SHAP explanations are not available for these models'}
          </span>
        </div>
      </div>
    </div>
  );
}

export default ModelReport;
