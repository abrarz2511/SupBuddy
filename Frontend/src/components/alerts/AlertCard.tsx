import {
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  Error as ErrorIcon,
  Psychology as AnalysisIcon,
  Schedule as ScheduleIcon,
  ChevronRight as ChevronRightIcon,
} from '@mui/icons-material';
import { Alert, ALERT_TYPE_CONFIG } from '@/types';
import { StatusBadge } from '@/components/common/StatusBadge';
import { formatDistanceToNow } from 'date-fns';

interface AlertCardProps {
  alert: Alert;
  onClick?: () => void;
  showShipmentInfo?: boolean;
}

/**
 * AlertCard Component
 * Displays an alert with priority, type, and analysis status
 */
export function AlertCard({ alert, onClick, showShipmentInfo = true }: AlertCardProps) {
  const typeConfig = ALERT_TYPE_CONFIG[alert.alert_type];
  const hasAnalysis = alert.analysis !== undefined && alert.analysis !== null;

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
        position: 'relative',
      }}
      onClick={onClick}
    >
      <CardContent>
        {/* Header with priority and status */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <StatusBadge status={alert.priority} type="priority" />
            <StatusBadge status={alert.status} type="alert" />
          </Box>
          {onClick && (
            <IconButton size="small">
              <ChevronRightIcon />
            </IconButton>
          )}
        </Box>

        {/* Alert Type */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <ErrorIcon sx={{ fontSize: 20, color: 'error.main' }} />
          <Typography variant="subtitle2" fontWeight={600}>
            {typeConfig.label}
          </Typography>
        </Box>

        {/* Alert Description */}
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {alert.backend_reason}
        </Typography>

        {/* Shipment Info */}
        {showShipmentInfo && alert.shipment && (
          <Box sx={{ mb: 2 }}>
            <Chip
              label={`Tracking: ${alert.shipment.tracking_number}`}
              size="small"
              variant="outlined"
              sx={{ fontSize: '0.7rem' }}
            />
          </Box>
        )}

        {/* Delay Info */}
        {alert.delay_minutes && (
          <Typography variant="caption" color="error.main" sx={{ display: 'block', mb: 1, fontWeight: 600 }}>
            Delayed by {Math.floor(alert.delay_minutes / 60)}h {alert.delay_minutes % 60}m
          </Typography>
        )}

        {/* Analysis Status */}
        {hasAnalysis && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
            <AnalysisIcon sx={{ fontSize: 16, color: 'secondary.main' }} />
            <Typography variant="caption" color="secondary.main" fontWeight={600}>
              AI Analysis Available
            </Typography>
          </Box>
        )}

        {/* Detected Time */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <ScheduleIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
          <Typography variant="caption" color="text.secondary">
            Detected {formatDistanceToNow(new Date(alert.detected_at), { addSuffix: true })}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

// Made with Bob