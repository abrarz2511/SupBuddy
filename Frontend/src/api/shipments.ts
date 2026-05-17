import apiClient, { apiCall } from './client';
import { Shipment, Milestone } from '@/types';
import { API_CONFIG } from '@/config/api.config';

/**
 * Paginated response type
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Shipments API Service
 * Handles all shipment-related API calls
 */
export const shipmentsApi = {
  /**
   * Get all shipments with pagination
   */
  getAll: async (page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<Shipment>> => {
    return apiCall(() =>
      apiClient.get<PaginatedResponse<Shipment>>(API_CONFIG.endpoints.shipments, {
        params: { page, page_size: pageSize },
      })
    );
  },

  /**
   * Get active shipments (not delivered)
   */
  getActiveShipments: async (): Promise<Shipment[]> => {
    return apiCall(() =>
      apiClient.get<Shipment[]>(`${API_CONFIG.endpoints.shipments}/active`)
    );
  },

  /**
   * Get a single shipment by tracking number
   */
  getByTrackingNumber: async (trackingNumber: string): Promise<Shipment> => {
    return apiCall(() =>
      apiClient.get<Shipment>(`${API_CONFIG.endpoints.shipments}/tracking/${trackingNumber}`)
    );
  },

  /**
   * Get a single shipment by ID
   */
  getById: async (shipmentId: string): Promise<Shipment> => {
    return apiCall(() =>
      apiClient.get<Shipment>(`${API_CONFIG.endpoints.shipments}/${shipmentId}`)
    );
  },

  /**
   * Create a new shipment
   */
  create: async (shipmentData: Partial<Shipment>): Promise<Shipment> => {
    return apiCall(() =>
      apiClient.post<Shipment>(API_CONFIG.endpoints.shipments, shipmentData)
    );
  },

  /**
   * Update a shipment by tracking number
   */
  update: async (trackingNumber: string, shipmentData: Partial<Shipment>): Promise<Shipment> => {
    return apiCall(() =>
      apiClient.patch<Shipment>(
        `${API_CONFIG.endpoints.shipments}/tracking/${trackingNumber}`,
        shipmentData
      )
    );
  },

  /**
   * Add a milestone to a shipment
   */
  addMilestone: async (
    shipmentId: string,
    milestoneData: Partial<Milestone>
  ): Promise<Milestone> => {
    return apiCall(() =>
      apiClient.post<Milestone>(
        `${API_CONFIG.endpoints.shipments}/${shipmentId}/milestones`,
        milestoneData
      )
    );
  },

  /**
   * Get shipment timeline (milestones)
   */
  getTimeline: async (shipmentId: string): Promise<Milestone[]> => {
    return apiCall(() =>
      apiClient.get<Milestone[]>(
        `${API_CONFIG.endpoints.shipments}/${shipmentId}/milestones`
      )
    );
  },
};

export default shipmentsApi;

// Made with Bob
