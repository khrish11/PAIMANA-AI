import { useState, useEffect, useCallback } from 'react';

// Simple in-memory cache
const nidCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export function useNID(projectId) {
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
      const cached = nidCache.get(projectId);
      if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        setData(cached.data);
        setLoading(false);
        return;
      }
      
      const response = await fetch(`/api/projects/${projectId}/nid`);
      if (!response.ok) {
        throw new Error('Failed to fetch NID data');
      }
      
      const nidData = await response.json();
      
      // Cache the result
      nidCache.set(projectId, {
        data: nidData,
        timestamp: Date.now(),
      });
      
      setData(nidData);
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
      nidCache.delete(projectId);
      fetchData();
    }
  };

  const invalidateCache = () => {
    if (projectId) {
      nidCache.delete(projectId);
    }
  };

  return { data, loading, error, retry, invalidateCache };
}
