import { useState, useEffect, useCallback } from 'react';
import {
  getProjectRisk,
  getProjectNID,
  getProjectPBE,
  getProjectRCF,
  getProjectTrend,
  getProjectNetwork,
} from '../services/api';

// Simple in-memory cache
const intelligenceCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export function useProjectIntelligence(projectId) {
  const [data, setData] = useState({
    project: null,
    risk: null,
    nid: null,
    pbe: null,
    rcf: null,
    trend: null,
    network: null,
  });
  const [loading, setLoading] = useState({
    overall: true,
    risk: true,
    nid: true,
    pbe: true,
    rcf: true,
    trend: true,
    network: true,
  });
  const [error, setError] = useState({
    overall: null,
    risk: null,
    nid: null,
    pbe: null,
    rcf: null,
    trend: null,
    network: null,
  });
  const [availability, setAvailability] = useState({
    risk: 'unknown',
    nid: 'unknown',
    pbe: 'unknown',
    rcf: 'unknown',
    trend: 'unknown',
    network: 'unknown',
  });

  const fetchData = useCallback(async () => {
    if (!projectId) {
      setLoading({ overall: false, risk: false, nid: false, pbe: false, rcf: false, trend: false, network: false });
      return;
    }

    setLoading(prev => ({ ...prev, overall: true }));
    setError(prev => ({ ...prev, overall: null }));

    // Check cache first
    const cached = intelligenceCache.get(projectId);
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      setData(cached.data);
      setAvailability(cached.availability);
      setLoading({ overall: false, risk: false, nid: false, pbe: false, rcf: false, trend: false, network: false });
      return;
    }

    // Fetch all intelligence in parallel using Promise.allSettled for graceful degradation
    const results = await Promise.allSettled([
      getProjectRisk(projectId).catch(err => ({ error: err.message })),
      getProjectNID(projectId).catch(err => ({ error: err.message })),
      getProjectPBE(projectId).catch(err => ({ error: err.message })),
      getProjectRCF(projectId).catch(err => ({ error: err.message })),
      getProjectTrend(projectId).catch(err => ({ error: err.message })),
      getProjectNetwork(projectId).catch(err => ({ error: err.message })),
    ]);

    const [riskResult, nidResult, pbeResult, rcfResult, trendResult, networkResult] = results;

    const newData = {
      project: null,
      risk: null,
      nid: null,
      pbe: null,
      rcf: null,
      trend: null,
      network: null,
    };
    const newLoading = {
      overall: false,
      risk: false,
      nid: false,
      pbe: false,
      rcf: false,
      trend: false,
      network: false,
    };
    const newError = {
      overall: null,
      risk: null,
      nid: null,
      pbe: null,
      rcf: null,
      trend: null,
      network: null,
    };
    const newAvailability = {
      risk: 'unknown',
      nid: 'unknown',
      pbe: 'unknown',
      rcf: 'unknown',
      trend: 'unknown',
      network: 'unknown',
    };

    // Risk
    if (riskResult.status === 'fulfilled' && !riskResult.value.error) {
      newData.risk = riskResult.value;
      newLoading.risk = false;
      newError.risk = null;
      newAvailability.risk = 'available';
    } else if (riskResult.status === 'rejected' || riskResult.value.error) {
      newData.risk = null;
      newLoading.risk = false;
      newError.risk = riskResult.reason?.message || riskResult.value.error || 'Failed to load risk data';
      newAvailability.risk = 'error';
    }

    // NID
    if (nidResult.status === 'fulfilled' && !nidResult.value.error) {
      newData.nid = nidResult.value;
      newLoading.nid = false;
      newError.nid = null;
      newAvailability.nid = nidResult.value.available === false ? 'unavailable' : 'available';
    } else if (nidResult.status === 'rejected' || nidResult.value.error) {
      newData.nid = null;
      newLoading.nid = false;
      newError.nid = nidResult.reason?.message || nidResult.value.error || 'Failed to load NID data';
      newAvailability.nid = 'error';
    }

    // PBE
    if (pbeResult.status === 'fulfilled' && !pbeResult.value.error) {
      newData.pbe = pbeResult.value;
      newLoading.pbe = false;
      newError.pbe = null;
      newAvailability.pbe = pbeResult.value.available === false ? 'unavailable' : 'available';
    } else if (pbeResult.status === 'rejected' || pbeResult.value.error) {
      newData.pbe = null;
      newLoading.pbe = false;
      newError.pbe = pbeResult.reason?.message || pbeResult.value.error || 'Failed to load PBE data';
      newAvailability.pbe = 'error';
    }

    // RCF
    if (rcfResult.status === 'fulfilled' && !rcfResult.value.error) {
      newData.rcf = rcfResult.value;
      newLoading.rcf = false;
      newError.rcf = null;
      newAvailability.rcf = rcfResult.value.available === false ? 'unavailable' : 'available';
    } else if (rcfResult.status === 'rejected' || rcfResult.value.error) {
      newData.rcf = null;
      newLoading.rcf = false;
      newError.rcf = rcfResult.reason?.message || rcfResult.value.error || 'Failed to load RCF data';
      newAvailability.rcf = 'error';
    }

    // Trend
    if (trendResult.status === 'fulfilled' && !trendResult.value.error) {
      newData.trend = trendResult.value;
      newLoading.trend = false;
      newError.trend = null;
      newAvailability.trend = 'available';
    } else if (trendResult.status === 'rejected' || trendResult.value.error) {
      newData.trend = null;
      newLoading.trend = false;
      newError.trend = trendResult.reason?.message || trendResult.value.error || 'Failed to load trend data';
      newAvailability.trend = 'error';
    }

    // Network
    if (networkResult.status === 'fulfilled' && !networkResult.value.error) {
      newData.network = networkResult.value;
      newLoading.network = false;
      newError.network = null;
      newAvailability.network = networkResult.value.available === false ? 'unavailable' : 'available';
    } else if (networkResult.status === 'rejected' || networkResult.value.error) {
      newData.network = null;
      newLoading.network = false;
      newError.network = networkResult.reason?.message || networkResult.value.error || 'Failed to load network data';
      newAvailability.network = 'error';
    }

    setData(newData);
    setLoading(newLoading);
    setError(newError);
    setAvailability(newAvailability);

    // Cache the result
    intelligenceCache.set(projectId, {
      data: newData,
      availability: newAvailability,
      timestamp: Date.now(),
    });
  }, [projectId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const retry = useCallback(() => {
    if (projectId) {
      intelligenceCache.delete(projectId);
      fetchData();
    }
  }, [projectId, fetchData]);

  const invalidateCache = useCallback(() => {
    if (projectId) {
      intelligenceCache.delete(projectId);
    }
  }, [projectId]);

  // Derived: overall availability
  const availableLayers = Object.values(availability).filter(
    status => status === 'available'
  ).length;
  const totalLayers = Object.keys(availability).length;

  return {
    data,
    loading,
    error,
    availability,
    availableLayers,
    totalLayers,
    retry,
    invalidateCache,
  };
}
