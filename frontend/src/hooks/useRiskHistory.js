import { useState, useEffect, useCallback } from 'react';
import { getProjectRisk } from '../services/api';

// Simple in-memory cache
const historyCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export function useRiskHistory(projectId) {
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
      
      // Check cache first
      const cached = historyCache.get(projectId);
      if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        setData(cached.data);
        setLoading(false);
        return;
      }
      
      const riskData = await getProjectRisk(projectId);
      
      // Derive history from risk data (backend may not have dedicated history endpoint)
      const historyData = riskData?.history || [];
      
      // Cache the result
      historyCache.set(projectId, {
        data: historyData,
        timestamp: Date.now(),
      });
      
      setData(historyData);
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
    if (projectId) {
      historyCache.delete(projectId);
      fetchData();
    }
  };

  const invalidateCache = () => {
    if (projectId) {
      historyCache.delete(projectId);
    }
  };

  return { data, loading, error, retry, invalidateCache };
}
