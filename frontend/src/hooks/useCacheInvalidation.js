// Simple cache invalidation utility
// This provides a centralized way to invalidate caches after data mutations

const cacheInvalidators = new Map();
const listeners = new Set();

export function registerCacheInvalidator(key, invalidator) {
  cacheInvalidators.set(key, invalidator);
}

export function invalidateCache(key) {
  const invalidator = cacheInvalidators.get(key);
  if (invalidator) {
    invalidator();
  }
  
  // Notify listeners
  listeners.forEach(listener => listener(key));
}

export function subscribeToInvalidations(callback) {
  listeners.add(callback);
  return () => listeners.delete(callback);
}

// Invalidate multiple caches at once
export function invalidateCaches(keys) {
  keys.forEach(key => invalidateCache(key));
}

// Predefined cache keys for common operations
export const CACHE_KEYS = {
  PROJECTS: 'projects',
  PROJECT_RISK: 'project_risk',
  PROJECT_HISTORY: 'project_history',
  DASHBOARD_STATS: 'dashboard_stats',
  IMPORT_BATCHES: 'import_batches',
  SUBMISSIONS: 'submissions',
  RISK_HISTORY: 'risk_history',
  NID: 'nid',
  PBE: 'pbe',
  RCF: 'rcf',
  ANOMALIES: 'anomalies',
  GOVERNANCE: 'governance',
};

// Cache invalidation helpers for specific operations
export function invalidateAfterProjectCreation() {
  invalidateCaches([
    CACHE_KEYS.PROJECTS,
    CACHE_KEYS.DASHBOARD_STATS,
  ]);
}

export function invalidateAfterSubmission(projectId) {
  invalidateCaches([
    CACHE_KEYS.PROJECT_RISK,
    CACHE_KEYS.PROJECT_HISTORY,
    CACHE_KEYS.RISK_HISTORY,
    CACHE_KEYS.DASHBOARD_STATS,
    CACHE_KEYS.SUBMISSIONS,
  ]);
  
  // Invalidate project-specific caches
  if (projectId) {
    invalidateCache(`${CACHE_KEYS.PROJECT_RISK}:${projectId}`);
    invalidateCache(`${CACHE_KEYS.PROJECT_HISTORY}:${projectId}`);
  }
}

export function invalidateAfterBulkImport() {
  invalidateCaches([
    CACHE_KEYS.PROJECTS,
    CACHE_KEYS.PROJECT_RISK,
    CACHE_KEYS.PROJECT_HISTORY,
    CACHE_KEYS.DASHBOARD_STATS,
    CACHE_KEYS.IMPORT_BATCHES,
    CACHE_KEYS.SUBMISSIONS,
  ]);
}

export function invalidateAfterRevision(projectId) {
  invalidateCaches([
    CACHE_KEYS.PROJECT_RISK,
    CACHE_KEYS.PROJECT_HISTORY,
    CACHE_KEYS.RISK_HISTORY,
    CACHE_KEYS.DASHBOARD_STATS,
  ]);
  
  if (projectId) {
    invalidateCache(`${CACHE_KEYS.PROJECT_RISK}:${projectId}`);
    invalidateCache(`${CACHE_KEYS.PROJECT_HISTORY}:${projectId}`);
  }
}
