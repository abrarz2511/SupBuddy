import apiClient, { apiCall } from './client';
import { Alert, AlertWithAnalysis, AlertAnalysis } from '@/types';
import { API_CONFIG } from '@/config/api.config';

/**
 * Alert query parameters
 */
export interface AlertQueryParams {
  shipment_id?: string;
  status?: string;
  priority?: string;
  alert_type?: string;
  from_date?: string;
  to_date?: string;
  limit?: number;
  offset?: number;
  include_analysis?: boolean;
}

/**
 * Alerts API Service
 * Handles all alert-related API calls
 */
export const alertsApi = {
  /**
   * Get all alerts with optional filters
   */
  getAll: async (params?: AlertQueryParams): Promise<Alert[]> => {
    return apiCall(() =>
      apiClient.get<Alert[]>(API_CONFIG.endpoints.alerts, { params })
    );
  },

  /**
   * Get a single alert by ID with full analysis
   */
  getById: async (alertId: string): Promise<AlertWithAnalysis> => {
    return apiCall(() =>
      apiClient.get<AlertWithAnalysis>(`${API_CONFIG.endpoints.alerts}/${alertId}`)
    );
  },

  /**
   * Get active alerts (OPEN, ANALYZING, ANALYZED)
   */
  getActiveAlerts: async (): Promise<Alert[]> => {
    return apiCall(() =>
      apiClient.get<Alert[]>(API_CONFIG.endpoints.alerts, {
        params: {
          status: 'OPEN,ANALYZING,ANALYZED',
          limit: 100,
        },
      })
    );
  },

  /**
   * Get alerts by priority
   */
  getByPriority: async (priority: string): Promise<Alert[]> => {
    return apiCall(() =>
      apiClient.get<Alert[]>(API_CONFIG.endpoints.alerts, {
        params: {
          priority,
          status: 'OPEN,ANALYZING,ANALYZED',
        },
      })
    );
  },

  /**
   * Get alerts for a specific shipment
   */
  getByShipment: async (shipmentId: string): Promise<AlertWithAnalysis[]> => {
    return apiCall(() =>
      apiClient.get<AlertWithAnalysis[]>(
        `${API_CONFIG.endpoints.alerts}/shipments/${shipmentId}/alerts`
      )
    );
  },

  /**
   * Trigger AI agent analysis for an alert
   */
  triggerAnalysis: async (alertId: string): Promise<AlertWithAnalysis> => {
    return apiCall(() =>
      apiClient.post<AlertWithAnalysis>(`${API_CONFIG.endpoints.alerts}/${alertId}/analyze`)
    );
  },

  /**
   * Analyze pending alerts in batch
   */
  analyzePending: async (maxAlerts: number = 10): Promise<{ analyzed_count: number; alert_ids: string[] }> => {
    return apiCall(() =>
      apiClient.post(`${API_CONFIG.endpoints.alerts}/analyze-pending`, null, {
        params: { max_alerts: maxAlerts },
      })
    );
  },

  /**
   * Update alert status
   */
  updateStatus: async (
    alertId: string,
    newStatus: string,
    resolvedAt?: string
  ): Promise<Alert> => {
    return apiCall(() =>
      apiClient.patch<Alert>(`${API_CONFIG.endpoints.alerts}/${alertId}/status`, null, {
        params: { new_status: newStatus, resolved_at: resolvedAt },
      })
    );
  },

  /**
   * Get alert statistics
   */
  getStats: async (shipmentId?: string): Promise<Record<string, any>> => {
    return apiCall(() =>
      apiClient.get(`${API_CONFIG.endpoints.alerts}/statistics/summary`, {
        params: shipmentId ? { shipment_id: shipmentId } : undefined,
      })
    );
  },
};

export default alertsApi;

// Made with Bob
