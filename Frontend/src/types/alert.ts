import { Shipment } from './shipment';

// Alert type enumeration
export type AlertType =
  | 'MISSING_UPDATE'
  | 'LATE_ARRIVAL'
  | 'STALE_STATUS'
  | 'CUSTOMS_DELAY'
  | 'LOCATION_MISMATCH';

// Alert priority levels
export type AlertPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

// Alert status
export type AlertStatus =
  | 'OPEN'
  | 'ANALYZING'
  | 'ANALYZED'
  | 'RESOLVED'
  | 'CLOSED';

// Main Alert interface
export interface Alert {
  id: string;
  shipment_id: string;
  sla_rule_id: string;
  alert_type: AlertType;
  priority: AlertPriority;
  status: AlertStatus;
  detected_at: string;
  resolved_at?: string;
  backend_reason: string;
  milestone_type: string;
  delay_minutes?: number;
  shipment?: Shipment;
  analysis?: AlertAnalysis;
}

// Alert Analysis from AI Agent
export interface AlertAnalysis {
  id: string;
  alert_id: string;
  likely_cause: string;
  risk_priority: AlertPriority;
  confidence_level: number; // 0.0 to 1.0
  supporting_evidence: Record<string, any>;
  external_factors: Record<string, any>;
  recommended_action?: string;
  analyzed_at: string;
  agent_version: string;
}

// Alert with full analysis details
export interface AlertWithAnalysis extends Alert {
  analysis: AlertAnalysis;
}

// Query parameters for alerts
export interface AlertQueryParams {
  shipment_id?: string;
  status?: string; // Comma-separated statuses
  priority?: string; // Comma-separated priorities
  alert_type?: AlertType;
  from_date?: string;
  to_date?: string;
  skip?: number;
  limit?: number;
}

// Alert filter state
export interface AlertFilters {
  status: AlertStatus[];
  priority: AlertPriority[];
  alertType?: AlertType;
  dateRange?: {
    from: string;
    to: string;
  };
}

// Priority configuration for UI
export interface AlertPriorityConfig {
  label: string;
  color: string;
  bgColor: string;
  icon: string;
  severity: number; // 1-4, higher is more severe
}

export const ALERT_PRIORITY_CONFIG: Record<AlertPriority, AlertPriorityConfig> = {
  LOW: {
    label: 'Low',
    color: '#1976d2',
    bgColor: '#e3f2fd',
    icon: 'info',
    severity: 1,
  },
  MEDIUM: {
    label: 'Medium',
    color: '#fbc02d',
    bgColor: '#fffde7',
    icon: 'warning',
    severity: 2,
  },
  HIGH: {
    label: 'High',
    color: '#f57c00',
    bgColor: '#fff3e0',
    icon: 'error',
    severity: 3,
  },
  CRITICAL: {
    label: 'Critical',
    color: '#d32f2f',
    bgColor: '#ffebee',
    icon: 'report',
    severity: 4,
  },
};

// Alert type configuration
export interface AlertTypeConfig {
  label: string;
  description: string;
  icon: string;
}

export const ALERT_TYPE_CONFIG: Record<AlertType, AlertTypeConfig> = {
  MISSING_UPDATE: {
    label: 'Missing Update',
    description: 'Expected milestone update not received',
    icon: 'event_busy',
  },
  LATE_ARRIVAL: {
    label: 'Late Arrival',
    description: 'Milestone received later than expected',
    icon: 'schedule',
  },
  STALE_STATUS: {
    label: 'Stale Status',
    description: 'No updates for extended period',
    icon: 'update_disabled',
  },
  CUSTOMS_DELAY: {
    label: 'Customs Delay',
    description: 'Customs clearance taking too long',
    icon: 'gavel',
  },
  LOCATION_MISMATCH: {
    label: 'Location Mismatch',
    description: 'Shipment at unexpected location',
    icon: 'wrong_location',
  },
};

// Alert status configuration
export interface AlertStatusConfig {
  label: string;
  color: string;
  icon: string;
}

export const ALERT_STATUS_CONFIG: Record<AlertStatus, AlertStatusConfig> = {
  OPEN: {
    label: 'Open',
    color: '#f44336',
    icon: 'error_outline',
  },
  ANALYZING: {
    label: 'Analyzing',
    color: '#ff9800',
    icon: 'psychology',
  },
  ANALYZED: {
    label: 'Analyzed',
    color: '#2196f3',
    icon: 'analytics',
  },
  RESOLVED: {
    label: 'Resolved',
    color: '#4caf50',
    icon: 'check_circle',
  },
  CLOSED: {
    label: 'Closed',
    color: '#9e9e9e',
    icon: 'cancel',
  },
};

// Made with Bob
