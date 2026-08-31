import { useState, useEffect, useCallback } from 'react';
import { getProjectNetwork, getNetwork, getBlastRadius } from '../services/api';

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export function useNetworkIntelligence(projectId = null) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cache, setCache] = useState(new Map());
  const [lastFetch, setLastFetch] = useState(null);

  const fetchNetwork = useCallback(async () => {
    setLoading(true);
    setError(null);

    const cacheKey = projectId ? `network-${projectId}` : 'network-global';
    const cached = cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      setData(cached.data);
      setLoading(false);
      setLastFetch(cached.timestamp);
      return;
    }

    try {
      const networkData = projectId 
        ? await getProjectNetwork(projectId)
        : await getNetwork();

      const cacheEntry = {
        data: networkData,
        timestamp: Date.now()
      };

      setCache(prev => new Map(prev).set(cacheKey, cacheEntry));
      setData(networkData);
      setLastFetch(cacheEntry.timestamp);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [projectId, cache]);

  const fetchBlastRadius = useCallback(async (depth = 2, relationshipTypes = null, riskThreshold = 'HIGH') => {
    if (!projectId) {
      throw new Error('Project ID is required for blast radius analysis');
    }

    try {
      const blastData = await getBlastRadius(projectId, depth, relationshipTypes, riskThreshold);
      return blastData;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [projectId]);

  const retry = useCallback(() => {
    const cacheKey = projectId ? `network-${projectId}` : 'network-global';
    setCache(prev => {
      const newCache = new Map(prev);
      newCache.delete(cacheKey);
      return newCache;
    });
    fetchNetwork();
  }, [projectId, fetchNetwork]);

  const invalidateCache = useCallback(() => {
    setCache(new Map());
  }, []);

  useEffect(() => {
    fetchNetwork();
  }, [fetchNetwork]);

  return {
    data,
    loading,
    error,
    available: data?.available || false,
    nodes: data?.nodes || [],
    edges: data?.edges || [],
    metadata: data?.metadata || {},
    fetchBlastRadius,
    retry,
    invalidateCache,
    lastFetch
  };
}
