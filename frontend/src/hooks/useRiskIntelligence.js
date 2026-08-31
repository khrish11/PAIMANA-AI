import { useState, useEffect, useCallback, useMemo } from 'react';
import { getDashboard, getProjects } from '../services/api';

export function useRiskIntelligence(filters = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const filtersString = useMemo(() => JSON.stringify(filters), [filters]);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const parsedFilters = JSON.parse(filtersString);
      const dashboardData = await getDashboard();
      const projectsData = await getProjects(parsedFilters);
      setData({
        dashboard: dashboardData,
        projects: projectsData.projects || [],
        total_count: projectsData.total_count || 0,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filtersString]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const retry = () => {
    fetchData();
  };

  return { data, loading, error, retry };
}
