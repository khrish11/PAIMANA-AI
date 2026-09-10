import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createProjectData } from '../services/api';
import { invalidateAfterProjectCreation } from '../hooks';

function NewProject() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    // Step 1: Project Information
    project_name: '',
    project_code: '',
    ministry: '',
    sector: '',
    state: '',
    department: '',
    implementing_agency: '',
    // Step 2: Cost
    sanctioned_cost: '',
    // Step 3: Schedule
    approved_date: '',
    original_completion_date: '',
    revised_completion_date: '',
    // Step 4: Initial Monitoring
    reporting_month: '',
    initial_expenditure: '',
    initial_physical_progress: '',
    initial_narrative: '',
    // Step 5: Status
    status: 'ONGOING',
  });

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const nextStep = () => setStep(prev => prev + 1);
  const prevStep = () => setStep(prev => prev - 1);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const projectData = {
        project_code: formData.project_code,
        project_name: formData.project_name,
        ministry: formData.ministry,
        sector: formData.sector,
        state: formData.state,
        implementing_agency: formData.implementing_agency,
        department: formData.department,
        sanctioned_cost: formData.sanctioned_cost ? parseFloat(formData.sanctioned_cost) : null,
        approved_date: formData.approved_date ? new Date(formData.approved_date).toISOString().split('T')[0] : null,
        original_completion_date: formData.original_completion_date ? new Date(formData.original_completion_date).toISOString().split('T')[0] : null,
        revised_completion_date: formData.revised_completion_date ? new Date(formData.revised_completion_date).toISOString().split('T')[0] : null,
        data_source: 'manual',
        import_method: 'manual',
        provenance_status: 'verified',
      };

      const result = await createProjectData(projectData);
      
      // Invalidate caches
      invalidateAfterProjectCreation();
      
      navigate('/data-management');
    } catch (err) {
      setError(err.message || 'Failed to create project');
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Create New Project</h1>
        <p className="text-gray-600 mt-2">Step {step} of 5</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          <span className="text-sm font-medium">Project Info</span>
          <span className="text-sm font-medium">Cost</span>
          <span className="text-sm font-medium">Schedule</span>
          <span className="text-sm font-medium">Monitoring</span>
          <span className="text-sm font-medium">Review</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${(step / 5) * 100}%` }}
          />
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Step 1: Project Information */}
        {step === 1 && (
          <div className="bg-white shadow rounded-lg p-6 border">
            <h2 className="text-xl font-semibold mb-4">Project Information</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Project Code (Unique)</label>
                <input
                  type="text"
                  name="project_code"
                  value={formData.project_code}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                  required
                  placeholder="e.g., P-2026-001"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Project Name</label>
                <input
                  type="text"
                  name="project_name"
                  value={formData.project_name}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                <input
                  type="text"
                  name="department"
                  value={formData.department}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ministry</label>
                <select
                  name="ministry"
                  value={formData.ministry}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                  required
                >
                  <option value="">Select Ministry</option>
                  <option value="Ministry of Road Transport">Ministry of Road Transport</option>
                  <option value="Ministry of Railways">Ministry of Railways</option>
                  <option value="Ministry of Power">Ministry of Power</option>
                  <option value="Ministry of Water Resources">Ministry of Water Resources</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Sector</label>
                <select
                  name="sector"
                  value={formData.sector}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                  required
                >
                  <option value="">Select Sector</option>
                  <option value="Roads">Roads</option>
                  <option value="Railways">Railways</option>
                  <option value="Power">Power</option>
                  <option value="Water">Water</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                <select
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                  required
                >
                  <option value="">Select State</option>
                  <option value="Maharashtra">Maharashtra</option>
                  <option value="Karnataka">Karnataka</option>
                  <option value="Tamil Nadu">Tamil Nadu</option>
                  <option value="Gujarat">Gujarat</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Implementing Agency</label>
                <input
                  type="text"
                  name="implementing_agency"
                  value={formData.implementing_agency}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                  required
                />
              </div>
            </div>
            <div className="mt-6 flex justify-end">
              <button type="button" onClick={nextStep} className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                Next
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Cost */}
        {step === 2 && (
          <div className="bg-white shadow rounded-lg p-6 border">
            <h2 className="text-xl font-semibold mb-4">Cost Information</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Sanctioned Cost (₹ Crores)</label>
                <input
                  type="number"
                  name="sanctioned_cost"
                  value={formData.sanctioned_cost}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                  required
                  min="0"
                  step="0.01"
                />
              </div>
            </div>
            <div className="mt-6 flex justify-between">
              <button type="button" onClick={prevStep} className="px-6 py-2 border rounded-md hover:bg-gray-50">
                Previous
              </button>
              <button type="button" onClick={nextStep} className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                Next
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Schedule */}
        {step === 3 && (
          <div className="bg-white shadow rounded-lg p-6 border">
            <h2 className="text-xl font-semibold mb-4">Schedule Information</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Approval Date</label>
                <input
                  type="date"
                  name="approved_date"
                  value={formData.approved_date}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Original Completion Date</label>
                <input
                  type="date"
                  name="original_completion_date"
                  value={formData.original_completion_date}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Revised Completion Date</label>
                <input
                  type="date"
                  name="revised_completion_date"
                  value={formData.revised_completion_date}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>
            </div>
            <div className="mt-6 flex justify-between">
              <button type="button" onClick={prevStep} className="px-6 py-2 border rounded-md hover:bg-gray-50">
                Previous
              </button>
              <button type="button" onClick={nextStep} className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                Next
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Initial Monitoring */}
        {step === 4 && (
          <div className="bg-white shadow rounded-lg p-6 border">
            <h2 className="text-xl font-semibold mb-4">Initial Monitoring Data</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Reporting Month</label>
                <input
                  type="month"
                  name="reporting_month"
                  value={formData.reporting_month}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Initial Expenditure (₹ Crores)</label>
                <input
                  type="number"
                  name="initial_expenditure"
                  value={formData.initial_expenditure}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                  min="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Initial Physical Progress (%)</label>
                <input
                  type="number"
                  name="initial_physical_progress"
                  value={formData.initial_physical_progress}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                  min="0"
                  max="100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Initial Narrative</label>
                <textarea
                  name="initial_narrative"
                  value={formData.initial_narrative}
                  onChange={handleChange}
                  className="w-full border rounded-md px-3 py-2"
                  rows="3"
                />
              </div>
            </div>
            <div className="mt-6 flex justify-between">
              <button type="button" onClick={prevStep} className="px-6 py-2 border rounded-md hover:bg-gray-50">
                Previous
              </button>
              <button type="button" onClick={nextStep} className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                Next
              </button>
            </div>
          </div>
        )}

        {/* Step 5: Review */}
        {step === 5 && (
          <div className="bg-white shadow rounded-lg p-6 border">
            <h2 className="text-xl font-semibold mb-4">Review and Submit</h2>
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded">
                <h3 className="font-medium mb-2">Project Information</h3>
                <p><strong>ID:</strong> {formData.project_id}</p>
                <p><strong>Name:</strong> {formData.project_name}</p>
                <p><strong>Ministry:</strong> {formData.ministry}</p>
                <p><strong>Sector:</strong> {formData.sector}</p>
                <p><strong>State:</strong> {formData.state}</p>
                <p><strong>Agency:</strong> {formData.implementing_agency}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <h3 className="font-medium mb-2">Cost</h3>
                <p><strong>Sanctioned:</strong> ₹{formData.sanctioned_cost} Cr</p>
                <p><strong>Revised:</strong> ₹{formData.revised_cost || 'N/A'} Cr</p>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <h3 className="font-medium mb-2">Schedule</h3>
                <p><strong>Approval:</strong> {formData.approval_date}</p>
                <p><strong>Original Completion:</strong> {formData.original_completion_date}</p>
                <p><strong>Planned Completion:</strong> {formData.planned_completion_date || 'N/A'}</p>
              </div>
              <div className="bg-yellow-50 border border-yellow-200 p-4 rounded">
                <p className="text-sm text-yellow-800">
                  <strong>Note:</strong> Risk calculation will be performed after sufficient monitoring data is available.
                </p>
              </div>
            </div>
            <div className="mt-6 flex justify-between">
              <button type="button" onClick={prevStep} className="px-6 py-2 border rounded-md hover:bg-gray-50">
                Previous
              </button>
              <button type="submit" disabled={loading} className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400">
                {loading ? 'Creating...' : 'Create Project'}
              </button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}

export default NewProject;
