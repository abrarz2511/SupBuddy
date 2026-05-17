import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  LocalShipping as ShippingIcon,
  LocationOn as LocationIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { Shipment, getShipmentStatusConfig } from '@/types';
import { StatusBadge } from '@/components/common/StatusBadge';
import { formatDistanceToNow } from 'date-fns';

interface ShipmentCardProps {
  shipment: Shipment;
  onClick?: () => void;
}

/**
 * ShipmentCard Component
 * Displays a shipment as a card in kanban-style layout
 */
export function ShipmentCard({ shipment, onClick }: ShipmentCardProps) {
  const statusConfig = getShipmentStatusConfig(shipment.current_status);
  
  // Calculate progress based on status
  const statusOrder = [
    'CREATED',
    'PORT_RECEIVED',
    'CUSTOMS_SUBMITTED',
    'CUSTOMS_CLEARED',
    'DELIVERY_CENTER_RECEIVED',
    'REGIONAL_HUB_RECEIVED',
    'OUT_FOR_DELIVERY',
    'DELIVERED',
  ];
  const currentIndex = statusOrder.indexOf(shipment.current_status);
  const progress =
    currentIndex >= 0 ? ((currentIndex + 1) / statusOrder.length) * 100 : 0;

  // Check if there are active alerts
  const hasAlerts = shipment.alert_count && shipment.alert_count > 0;

  return (
    <Card
      sx={{
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s',
        '&:hover': onClick
          ? {
              transform: 'translateY(-2px)',
              boxShadow: 4,
            }
          : {},
        borderLeft: `4px solid ${statusConfig.color}`,
        position: 'relative',
      }}
      onClick={onClick}
    >
      <CardContent>
        {/* Header with tracking number and alerts */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ShippingIcon sx={{ color: 'primary.main', fontSize: 20 }} />
            <Typography variant="subtitle2" fontWeight={600}>
              {shipment.tracking_number}
            </Typography>
          </Box>
          {hasAlerts && (
            <Tooltip title={`${shipment.alert_count} active alert(s)`}>
              <IconButton size="small" color="error">
                <WarningIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>

        {/* Status Badge */}
        <Box sx={{ mb: 2 }}>
          <StatusBadge status={shipment.current_status} type="shipment" />
        </Box>

        {/* Location */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <LocationIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="body2" color="text.secondary">
            {shipment.current_location || 'Location pending'}
          </Typography>
        </Box>

        {/* Route */}
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
          {shipment.origin} → {shipment.destination}
        </Typography>

        {/* Progress Bar */}
        <Box sx={{ mb: 1 }}>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              height: 6,
              borderRadius: 3,
              backgroundColor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                backgroundColor: statusConfig.color,
              },
            }}
          />
        </Box>

        {/* Last Updated */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <ScheduleIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
          <Typography variant="caption" color="text.secondary">
            Updated {formatDistanceToNow(new Date(shipment.updated_at), { addSuffix: true })}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

// Made with Bob
