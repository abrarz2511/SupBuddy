import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { shipmentsApi } from '@/api';
import { Shipment, Milestone } from '@/types';

/**
 * Hook to fetch all shipments with pagination
 */
export function useShipments(page: number = 1, pageSize: number = 20) {
  return useQuery({
    queryKey: ['shipments', 'paginated', page, pageSize],
    queryFn: () => shipmentsApi.getAll(page, pageSize),
    staleTime: 20000,
  });
}

/**
 * Hook to fetch active shipments (not delivered)
 */
export function useActiveShipments() {
  return useQuery({
    queryKey: ['shipments', 'active'],
    queryFn: () => shipmentsApi.getActiveShipments(),
    staleTime: 20000,
    refetchInterval: 30000, // Auto-refresh every 30 seconds
  });
}

/**
 * Hook to fetch a single shipment by tracking number
 */
export function useShipmentByTracking(trackingNumber: string) {
  return useQuery({
    queryKey: ['shipments', 'tracking', trackingNumber],
    queryFn: () => shipmentsApi.getByTrackingNumber(trackingNumber),
    enabled: !!trackingNumber,
    staleTime: 20000,
  });
}

/**
 * Hook to fetch a single shipment by ID
 */
export function useShipment(shipmentId: string) {
  return useQuery({
    queryKey: ['shipments', shipmentId],
    queryFn: () => shipmentsApi.getById(shipmentId),
    enabled: !!shipmentId,
    staleTime: 20000,
  });
}

/**
 * Hook to fetch shipment timeline (milestones)
 */
export function useShipmentTimeline(shipmentId: string) {
  return useQuery({
    queryKey: ['shipments', shipmentId, 'timeline'],
    queryFn: () => shipmentsApi.getTimeline(shipmentId),
    enabled: !!shipmentId,
    staleTime: 20000,
  });
}

/**
 * Hook to create a new shipment
 */
export function useCreateShipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (shipmentData: Partial<Shipment>) =>
      shipmentsApi.create(shipmentData),
    onSuccess: () => {
      // Invalidate and refetch shipments list
      queryClient.invalidateQueries({ queryKey: ['shipments'] });
    },
  });
}

/**
 * Hook to update a shipment
 */
export function useUpdateShipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      trackingNumber,
      data,
    }: {
      trackingNumber: string;
      data: Partial<Shipment>;
    }) => shipmentsApi.update(trackingNumber, data),
    onSuccess: (_, variables) => {
      // Invalidate shipment queries
      queryClient.invalidateQueries({
        queryKey: ['shipments', 'tracking', variables.trackingNumber],
      });
      queryClient.invalidateQueries({ queryKey: ['shipments'] });
    },
  });
}

/**
 * Hook to add a milestone to a shipment
 */
export function useAddMilestone() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      shipmentId,
      milestoneData,
    }: {
      shipmentId: string;
      milestoneData: Partial<Milestone>;
    }) => shipmentsApi.addMilestone(shipmentId, milestoneData),
    onSuccess: (_, variables) => {
      // Invalidate shipment and timeline queries
      queryClient.invalidateQueries({
        queryKey: ['shipments', variables.shipmentId],
      });
      queryClient.invalidateQueries({
        queryKey: ['shipments', variables.shipmentId, 'timeline'],
      });
      queryClient.invalidateQueries({ queryKey: ['shipments'] });
    },
  });
}

// Made with Bob