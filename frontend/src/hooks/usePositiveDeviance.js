import { useState, useEffect, useCallback } from 'react';
import {
  getPositiveDeviants,
  getPlaybooks,
  getPlaybookDetail,
  getSuggestedPlaybooks,
  dismissPlaybookSuggestion,
  markPlaybookSuggestionViewed,
} from '../services/api';

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export function usePositiveDeviance(projectId = null) {
  const [positiveDeviants, setPositiveDeviants] = useState(null);
  const [playbooks, setPlaybooks] = useState(null);
  const [suggestions, setSuggestions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cache, setCache] = useState(new Map());
  const [lastFetch, setLastFetch] = useState(null);

  const fetchPositiveDeviants = useCallback(async (filters = {}) => {
    setLoading(true);
    setError(null);

    const cacheKey = `positive-deviants-${JSON.stringify(filters)}`;
    const cached = cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      setPositiveDeviants(cached.data);
      setLoading(false);
      setLastFetch(cached.timestamp);
      return;
    }

    try {
      const data = await getPositiveDeviants(filters);

      const cacheEntry = {
        data,
        timestamp: Date.now()
      };

      setCache(prev => new Map(prev).set(cacheKey, cacheEntry));
      setPositiveDeviants(data);
      setLastFetch(cacheEntry.timestamp);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [cache]);

  const fetchPlaybooks = useCallback(async (filters = {}) => {
    setLoading(true);
    setError(null);

    const cacheKey = `playbooks-${JSON.stringify(filters)}`;
    const cached = cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      setPlaybooks(cached.data);
      setLoading(false);
      setLastFetch(cached.timestamp);
      return;
    }

    try {
      const data = await getPlaybooks(filters);

      const cacheEntry = {
        data,
        timestamp: Date.now()
      };

      setCache(prev => new Map(prev).set(cacheKey, cacheEntry));
      setPlaybooks(data);
      setLastFetch(cacheEntry.timestamp);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [cache]);

  const fetchPlaybookDetail = useCallback(async (playbookId) => {
    setLoading(true);
    setError(null);

    const cacheKey = `playbook-detail-${playbookId}`;
    const cached = cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      setLoading(false);
      return cached.data;
    }

    try {
      const data = await getPlaybookDetail(playbookId);

      const cacheEntry = {
        data,
        timestamp: Date.now()
      };

      setCache(prev => new Map(prev).set(cacheKey, cacheEntry));
      setLastFetch(cacheEntry.timestamp);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [cache]);

  const fetchSuggestions = useCallback(async (pid = null) => {
    const targetProjectId = pid || projectId;
    
    if (!targetProjectId) {
      throw new Error('Project ID is required for fetching suggestions');
    }

    setLoading(true);
    setError(null);

    const cacheKey = `suggestions-${targetProjectId}`;
    const cached = cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      setSuggestions(cached.data);
      setLoading(false);
      setLastFetch(cached.timestamp);
      return;
    }

    try {
      const data = await getSuggestedPlaybooks(targetProjectId);

      const cacheEntry = {
        data,
        timestamp: Date.now()
      };

      setCache(prev => new Map(prev).set(cacheKey, cacheEntry));
      setSuggestions(data);
      setLastFetch(cacheEntry.timestamp);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [projectId, cache]);

  const dismissSuggestion = useCallback(async (suggestionId) => {
    if (!projectId) {
      throw new Error('Project ID is required for dismissing suggestions');
    }

    try {
      await dismissPlaybookSuggestion(projectId, suggestionId);
      
      // Invalidate cache and refetch
      const cacheKey = `suggestions-${projectId}`;
      setCache(prev => {
        const newCache = new Map(prev);
        newCache.delete(cacheKey);
        return newCache;
      });
      
      await fetchSuggestions();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [projectId, fetchSuggestions]);

  const markSuggestionViewed = useCallback(async (suggestionId) => {
    if (!projectId) {
      throw new Error('Project ID is required for marking suggestions as viewed');
    }

    try {
      await markPlaybookSuggestionViewed(projectId, suggestionId);
      
      // Invalidate cache and refetch
      const cacheKey = `suggestions-${projectId}`;
      setCache(prev => {
        const newCache = new Map(prev);
        newCache.delete(cacheKey);
        return newCache;
      });
      
      await fetchSuggestions();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [projectId, fetchSuggestions]);

  const retry = useCallback(() => {
    setCache(new Map());
    fetchPositiveDeviants();
  }, [fetchPositiveDeviants]);

  const invalidateCache = useCallback(() => {
    setCache(new Map());
  }, []);

  useEffect(() => {
    if (projectId) {
      fetchSuggestions();
    }
  }, [projectId, fetchSuggestions]);

  return {
    positiveDeviants,
    playbooks,
    suggestions,
    loading,
    error,
    fetchPositiveDeviants,
    fetchPlaybooks,
    fetchPlaybookDetail,
    fetchSuggestions,
    dismissSuggestion,
    markSuggestionViewed,
    retry,
    invalidateCache,
    lastFetch,
  };
}
