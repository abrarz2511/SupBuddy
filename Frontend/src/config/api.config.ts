// API Configuration
export const API_CONFIG = {
  // Base URL for API requests
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  
  // Request timeout in milliseconds
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
  
  // Refresh intervals in milliseconds
  refreshInterval: parseInt(import.meta.env.VITE_REFRESH_INTERVAL || '30000'),
  alertRefreshInterval: parseInt(import.meta.env.VITE_ALERT_REFRESH_INTERVAL || '30000'),
  shipmentRefreshInterval: parseInt(import.meta.env.VITE_SHIPMENT_REFRESH_INTERVAL || '30000'),
  
  // Feature flags
  enableAutoRefresh: import.meta.env.VITE_ENABLE_AUTO_REFRESH === 'true',
  enableWebSocket: import.meta.env.VITE_ENABLE_WEBSOCKET === 'true',
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  
  // API endpoints
  endpoints: {
    shipments: '/api/v1/shipments',
    alerts: '/api/v1/alerts',
    schedules: '/api/v1/schedules',
    agent: '/api/v1/agent',
  },
  
  // Retry configuration
  retry: {
    maxRetries: 3,
    retryDelay: 1000, // milliseconds
    retryableStatuses: [408, 429, 500, 502, 503, 504],
  },
  
  // Cache configuration for React Query
  cache: {
    staleTime: 20000, // 20 seconds
    cacheTime: 300000, // 5 minutes
  },
  
  // Environment flags
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
};

// Made with Bob
