import { useState, useEffect, useCallback } from 'react';

// Simple in-memory cache
const pbeCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export function usePBE(projectId) {
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
      const cached = pbeCache.get(projectId);
      if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        setData(cached.data);
        setLoading(false);
        return;
      }
      
      const response = await fetch(`/api/projects/${projectId}/pbe`);
      if (!response.ok) {
        throw new Error('Failed to fetch PBE data');
      }
      
      const pbeData = await response.json();
      
      // Cache the result
      pbeCache.set(projectId, {
        data: pbeData,
        timestamp: Date.now(),
      });
      
      setData(pbeData);
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
      pbeCache.delete(projectId);
      fetchData();
    }
  };

  const invalidateCache = () => {
    if (projectId) {
      pbeCache.delete(projectId);
    }
  };

  return { data, loading, error, retry, invalidateCache };
}
