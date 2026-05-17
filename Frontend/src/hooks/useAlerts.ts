import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { alertsApi, AlertQueryParams } from '@/api/alerts';
import { Alert, AlertWithAnalysis } from '@/types';

/**
 * Hook to fetch all alerts with optional filters
 */
export function useAlerts(params?: AlertQueryParams) {
  return useQuery({
    queryKey: ['alerts', params],
    queryFn: () => alertsApi.getAll(params),
    staleTime: 20000,
    refetchInterval: 30000, // Auto-refresh every 30 seconds
  });
}

/**
 * Hook to fetch active alerts (OPEN, ANALYZING, ANALYZED)
 */
export function useActiveAlerts() {
  return useQuery({
    queryKey: ['alerts', 'active'],
    queryFn: () => alertsApi.getActiveAlerts(),
    staleTime: 20000,
    refetchInterval: 30000,
  });
}

/**
 * Hook to fetch a single alert by ID with analysis
 */
export function useAlert(alertId: string) {
  return useQuery({
    queryKey: ['alerts', alertId],
    queryFn: () => alertsApi.getById(alertId),
    enabled: !!alertId,
    staleTime: 20000,
  });
}

/**
 * Hook to fetch alerts by priority
 */
export function useAlertsByPriority(priority: string) {
  return useQuery({
    queryKey: ['alerts', 'priority', priority],
    queryFn: () => alertsApi.getByPriority(priority),
    enabled: !!priority,
    staleTime: 20000,
  });
}

/**
 * Hook to fetch alerts for a specific shipment
 */
export function useShipmentAlerts(shipmentId: string) {
  return useQuery({
    queryKey: ['alerts', 'shipment', shipmentId],
    queryFn: () => alertsApi.getByShipment(shipmentId),
    enabled: !!shipmentId,
    staleTime: 20000,
  });
}

/**
 * Hook to trigger AI analysis for an alert
 */
export function useAnalyzeAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: string) => alertsApi.triggerAnalysis(alertId),
    onSuccess: (data, alertId) => {
      // Invalidate alert queries
      queryClient.invalidateQueries({ queryKey: ['alerts', alertId] });
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
}

/**
 * Hook to analyze pending alerts in batch
 */
export function useAnalyzePendingAlerts() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (maxAlerts: number = 10) => alertsApi.analyzePending(maxAlerts),
    onSuccess: () => {
      // Invalidate all alert queries
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
}

/**
 * Hook to update alert status
 */
export function useUpdateAlertStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      alertId,
      status,
      resolvedAt,
    }: {
      alertId: string;
      status: string;
      resolvedAt?: string;
    }) => alertsApi.updateStatus(alertId, status, resolvedAt),
    onSuccess: (_, variables) => {
      // Invalidate alert queries
      queryClient.invalidateQueries({ queryKey: ['alerts', variables.alertId] });
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
}

/**
 * Hook to fetch alert statistics
 */
export function useAlertStats(shipmentId?: string) {
  return useQuery({
    queryKey: ['alerts', 'stats', shipmentId],
    queryFn: () => alertsApi.getStats(shipmentId),
    staleTime: 30000,
  });
}

// Made with Bob