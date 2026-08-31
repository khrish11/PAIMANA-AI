import { useState, useEffect, useCallback } from 'react';
import { getProjectRCF } from '../services/api';

export function useReferenceClass(projectId) {
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
        sector: rcfData.sector ?? null,
        size_band: rcfData.size_band ?? null,
        region: rcfData.state ?? null,
        comparable_count: rcfData.sample_count ?? null,
        current_percentile: rcfData.cost_overrun_p50 ?? null,
        cohort_median: rcfData.cost_overrun_p50 ?? null,
        p75: rcfData.cost_overrun_p80 ?? null,
        p90: rcfData.cost_overrun_p90 ?? null,
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
