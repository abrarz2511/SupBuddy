import apiClient, { apiCall } from './client';
import { Schedule } from '@/types';
import { API_CONFIG } from '@/config/api.config';

/**
 * Schedules API Service
 * Handles all schedule-related API calls
 */
export const schedulesApi = {
  /**
   * Get schedule for a specific shipment
   */
  getByShipmentId: async (shipmentId: string): Promise<Schedule[]> => {
    return apiCall(() =>
      apiClient.get<Schedule[]>(`${API_CONFIG.endpoints.schedules}/${shipmentId}`)
    );
  },

  /**
   * Create a schedule for a shipment
   */
  create: async (scheduleData: {
    shipment_id: string;
    milestones: Partial<Schedule>[];
  }): Promise<Schedule[]> => {
    return apiCall(() =>
      apiClient.post<Schedule[]>(API_CONFIG.endpoints.schedules, scheduleData)
    );
  },

  /**
   * Update a schedule milestone
   */
  update: async (scheduleId: string, scheduleData: Partial<Schedule>): Promise<Schedule> => {
    return apiCall(() =>
      apiClient.put<Schedule>(
        `${API_CONFIG.endpoints.schedules}/${scheduleId}`,
        scheduleData
      )
    );
  },

  /**
   * Delete a schedule
   */
  delete: async (scheduleId: string): Promise<void> => {
    return apiCall(() =>
      apiClient.delete(`${API_CONFIG.endpoints.schedules}/${scheduleId}`)
    );
  },
};

export default schedulesApi;

// Made with Bob
