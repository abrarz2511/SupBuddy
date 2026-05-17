import { Chip, ChipProps } from '@mui/material';
import {
  ShipmentStatus,
  getShipmentStatusConfig,
  AlertPriority,
  ALERT_PRIORITY_CONFIG,
  AlertStatus,
  ALERT_STATUS_CONFIG,
} from '@/types';

interface StatusBadgeProps extends Omit<ChipProps, 'label' | 'color'> {
  status: ShipmentStatus | AlertPriority | AlertStatus | string;
  type: 'shipment' | 'priority' | 'alert';
}

/**
 * StatusBadge Component
 * Displays a colored badge for shipment status, alert priority, or alert status
 */
export function StatusBadge({ status, type, ...props }: StatusBadgeProps) {
  let backgroundColor: string;
  let textColor: string;
  let label: string;
  
  if (type === 'shipment') {
    const config = getShipmentStatusConfig(status as ShipmentStatus);
    backgroundColor = config.color;
    textColor = '#fff';
    label = config.label;
  } else if (type === 'priority') {
    const config = ALERT_PRIORITY_CONFIG[status as AlertPriority];
    backgroundColor = config.bgColor;
    textColor = config.color;
    label = config.label;
  } else {
    const config = ALERT_STATUS_CONFIG[status as AlertStatus];
    backgroundColor = config.color;
    textColor = '#fff';
    label = config.label;
  }

  return (
    <Chip
      label={label}
      size="small"
      sx={{
        backgroundColor,
        color: textColor,
        fontWeight: 600,
        fontSize: '0.75rem',
        ...props.sx,
      }}
      {...props}
    />
  );
}

// Made with Bob
