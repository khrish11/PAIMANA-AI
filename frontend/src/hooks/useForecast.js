import { useState, useEffect, useCallback } from 'react';
import { getProjectRCF } from '../services/api';

export function useForecast(projectId) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    if (!projectId) {
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      setError(null);
      const rcfData = await getProjectRCF(projectId);
      setData({
        cost_forecast: rcfData.cost_overrun_p50 ?? null,
        completion_forecast: rcfData.schedule_delay_p50 ?? null,
        reference_class_comparison: rcfData.reference_class ?? null,
        sample_count: rcfData.sample_count ?? null,
        used_fallback: rcfData.used_fallback ?? false,
        warning: rcfData.warning ?? null,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const retry = () => {
    fetchData();
  };

  return { data, loading, error, retry };
}
