import { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  IconButton,
  Divider,
  Alert as MuiAlert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  ChevronRight as ChevronRightIcon,
  Dashboard as DashboardIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useActiveShipments, useActiveAlerts } from '@/hooks';
import { ShipmentCard } from '@/components/shipments';
import { AlertCard } from '@/components/alerts';
import { LoadingSpinner, EmptyState } from '@/components/common';

/**
 * Dashboard Page
 * Main dashboard showing active shipments, alerts, and quick actions
 */
export function Dashboard() {
  const navigate = useNavigate();
  const [showAllShipments, setShowAllShipments] = useState(false);

  // Fetch data
  const {
    data: shipments,
    isLoading: shipmentsLoading,
    error: shipmentsError,
    refetch: refetchShipments,
  } = useActiveShipments();

  const {
    data: alerts,
    isLoading: alertsLoading,
    error: alertsError,
    refetch: refetchAlerts,
  } = useActiveAlerts();

  // Limit shipments to 10 for dashboard view
  const displayedShipments = showAllShipments ? shipments : shipments?.slice(0, 10);
  const hasMoreShipments = shipments && shipments.length > 10;

  const handleRefresh = () => {
    refetchShipments();
    refetchAlerts();
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 3 }}>
      <Container maxWidth="xl">
        {/* Header */}
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <DashboardIcon sx={{ fontSize: 40, color: 'primary.main' }} />
            <Box>
              <Typography variant="h4" fontWeight={600}>
                SupBuddy Dashboard
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Real-time shipment tracking and AI-powered alerts
              </Typography>
            </Box>
          </Box>
          <IconButton onClick={handleRefresh} color="primary">
            <RefreshIcon />
          </IconButton>
        </Box>

        <Grid container spacing={3}>
          {/* Left Column - Shipments */}
          <Grid item xs={12} lg={7}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" fontWeight={600}>
                  📦 Active Shipments
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {shipments?.length || 0} active
                </Typography>
              </Box>

              {shipmentsLoading && <LoadingSpinner message="Loading shipments..." />}

              {shipmentsError && (
                <MuiAlert severity="error" sx={{ mb: 2 }}>
                  Failed to load shipments. Please try again.
                </MuiAlert>
              )}

              {!shipmentsLoading && !shipmentsError && displayedShipments && displayedShipments.length > 0 && (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {displayedShipments.map((shipment) => (
                    <ShipmentCard
                      key={shipment.id}
                      shipment={shipment}
                      onClick={() => navigate(`/shipments/${shipment.tracking_number}`)}
                    />
                  ))}

                  {hasMoreShipments && !showAllShipments && (
                    <Button
                      variant="outlined"
                      endIcon={<ChevronRightIcon />}
                      onClick={() => navigate('/manage-shipments')}
                      fullWidth
                    >
                      View All Shipments ({shipments.length})
                    </Button>
                  )}
                </Box>
              )}

              {!shipmentsLoading && !shipmentsError && (!displayedShipments || displayedShipments.length === 0) && (
                <EmptyState
                  title="No Active Shipments"
                  description="There are no active shipments at the moment. Create a new shipment to get started."
                  action={{
                    label: 'Create Shipment',
                    onClick: () => navigate('/manage-shipments'),
                  }}
                />
              )}
            </Paper>
          </Grid>

          {/* Right Column - Alerts and Actions */}
          <Grid item xs={12} lg={5}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {/* Quick Actions */}
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                  ⚡ Quick Actions
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => navigate('/manage-shipments?action=create')}
                    fullWidth
                    size="large"
                  >
                    Create New Shipment
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<EditIcon />}
                    onClick={() => navigate('/manage-shipments')}
                    fullWidth
                    size="large"
                  >
                    Manage Shipments
                  </Button>
                </Box>
              </Paper>

              {/* Alerts Section */}
              <Paper sx={{ p: 3, flexGrow: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h6" fontWeight={600}>
                    🚨 Active Alerts
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {alerts?.length || 0} alerts
                  </Typography>
                </Box>

                {alertsLoading && <LoadingSpinner message="Loading alerts..." />}

                {alertsError && (
                  <MuiAlert severity="error" sx={{ mb: 2 }}>
                    Failed to load alerts. Please try again.
                  </MuiAlert>
                )}

                {!alertsLoading && !alertsError && alerts && alerts.length > 0 && (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxHeight: 600, overflowY: 'auto' }}>
                    {alerts.slice(0, 5).map((alert) => (
                      <AlertCard
                        key={alert.id}
                        alert={alert}
                        onClick={() => navigate(`/alerts/${alert.id}`)}
                      />
                    ))}
                    {alerts.length > 5 && (
                      <Button
                        variant="text"
                        endIcon={<ChevronRightIcon />}
                        onClick={() => navigate('/alerts')}
                        fullWidth
                      >
                        View All Alerts ({alerts.length})
                      </Button>
                    )}
                  </Box>
                )}

                {!alertsLoading && !alertsError && (!alerts || alerts.length === 0) && (
                  <EmptyState
                    title="No Active Alerts"
                    description="All shipments are on track. No alerts at this time."
                  />
                )}
              </Paper>
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}

// Made with Bob