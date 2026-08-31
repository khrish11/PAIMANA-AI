import { useState, useEffect, useCallback } from 'react';
import { getProjectRisk } from '../services/api';

// Simple in-memory cache
const riskCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export function useProjectRisk(projectId) {
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
      const cached = riskCache.get(projectId);
      if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        setData(cached.data);
        setLoading(false);
        return;
      }
      
      const riskData = await getProjectRisk(projectId);
      
      // Cache the result
      riskCache.set(projectId, {
        data: riskData,
        timestamp: Date.now(),
      });
      
      setData(riskData);
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
    // Clear cache and retry
    if (projectId) {
      riskCache.delete(projectId);
      fetchData();
    }
  };

  const invalidateCache = () => {
    if (projectId) {
      riskCache.delete(projectId);
    }
  };

  return { data, loading, error, retry, invalidateCache };
}
