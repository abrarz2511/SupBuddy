// Shipment status types
export type ShipmentStatus =
  | 'CREATED'
  | 'PORT_RECEIVED'
  | 'CUSTOMS_SUBMITTED'
  | 'CUSTOMS_CLEARED'
  | 'DELIVERY_CENTER_RECEIVED'
  | 'REGIONAL_HUB_RECEIVED'
  | 'OUT_FOR_DELIVERY'
  | 'DELIVERED'
  | 'CANCELLED';

// Milestone interface
export interface Milestone {
  id: string;
  shipment_id: string;
  milestone_type: ShipmentStatus;
  location: string;
  status: string;
  received: boolean;
  approved: boolean;
  timestamp: string;
  notes?: string;
  created_at: string;
}

// Schedule interface
export interface Schedule {
  id: string;
  shipment_id: string;
  milestone_type: ShipmentStatus;
  expected_location: string;
  expected_arrival: string;
  expected_departure?: string;
  buffer_minutes: number;
  created_at: string;
}

// Main Shipment interface
export interface Shipment {
  id: string;
  tracking_number: string;
  current_status: ShipmentStatus | string;
  current_location?: string | null;
  origin: string;
  destination: string;
  customer_id?: string | null;
  created_at: string;
  updated_at: string;
  milestones?: Milestone[];
  schedules?: Schedule[];
  alert_count?: number;
}

// Query parameters for shipments
export interface ShipmentQueryParams {
  status?: string;
  customer_id?: string;
  from_date?: string;
  to_date?: string;
  skip?: number;
  limit?: number;
}

// Status display configuration
export interface ShipmentStatusConfig {
  label: string;
  color: string;
  icon: string;
  description: string;
}

export const SHIPMENT_STATUS_CONFIG: Record<ShipmentStatus, ShipmentStatusConfig> = {
  CREATED: {
    label: 'Created',
    color: '#607d8b',
    icon: 'add_box',
    description: 'Shipment has been created',
  },
  PORT_RECEIVED: {
    label: 'Port Received',
    color: '#2196f3',
    icon: 'anchor',
    description: 'Shipment received at port',
  },
  CUSTOMS_SUBMITTED: {
    label: 'Customs Submitted',
    color: '#ff9800',
    icon: 'assignment',
    description: 'Submitted to customs',
  },
  CUSTOMS_CLEARED: {
    label: 'Customs Cleared',
    color: '#4caf50',
    icon: 'check_circle',
    description: 'Cleared by customs',
  },
  DELIVERY_CENTER_RECEIVED: {
    label: 'Delivery Center',
    color: '#9c27b0',
    icon: 'warehouse',
    description: 'Received at delivery center',
  },
  REGIONAL_HUB_RECEIVED: {
    label: 'Regional Hub',
    color: '#00bcd4',
    icon: 'hub',
    description: 'Received at regional hub',
  },
  OUT_FOR_DELIVERY: {
    label: 'Out for Delivery',
    color: '#ff5722',
    icon: 'local_shipping',
    description: 'Out for final delivery',
  },
  DELIVERED: {
    label: 'Delivered',
    color: '#4caf50',
    icon: 'done_all',
    description: 'Delivered to customer',
  },
  CANCELLED: {
    label: 'Cancelled',
    color: '#757575',
    icon: 'cancel',
    description: 'Shipment was cancelled',
  },
};

export const UNKNOWN_SHIPMENT_STATUS_CONFIG: ShipmentStatusConfig = {
  label: 'Unknown',
  color: '#757575',
  icon: 'help',
  description: 'Shipment status is not recognized by the frontend',
};

export function getShipmentStatusConfig(status?: string | null): ShipmentStatusConfig {
  if (!status) {
    return UNKNOWN_SHIPMENT_STATUS_CONFIG;
  }

  return (
    SHIPMENT_STATUS_CONFIG[status as ShipmentStatus] ?? {
      ...UNKNOWN_SHIPMENT_STATUS_CONFIG,
      label: status
        .toLowerCase()
        .split('_')
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(' '),
    }
  );
}

// Made with Bob
