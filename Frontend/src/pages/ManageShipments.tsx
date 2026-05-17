import { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  TextField,
  Grid,
  Tabs,
  Tab,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert as MuiAlert,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useShipments, useCreateShipment, useUpdateShipment } from '@/hooks';
import { ShipmentCard } from '@/components/shipments';
import { LoadingSpinner, EmptyState } from '@/components/common';
import { ShipmentStatus, Shipment } from '@/types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const SHIPMENT_STATUS_OPTIONS: string[] = [
  'CREATED',
  'PORT_RECEIVED',
  'CUSTOMS_SUBMITTED',
  'CUSTOMS_CLEARED',
  'DELIVERY_CENTER_RECEIVED',
  'REGIONAL_HUB_RECEIVED',
  'OUT_FOR_DELIVERY',
  'DELIVERED',
  'CANCELLED',
];

const formatStatusLabel = (status: string) =>
  status
    .toLowerCase()
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');

const emptyEditShipment = {
  tracking_number: '',
  origin: '',
  destination: '',
  customer_id: '',
  current_location: '',
  current_status: 'CREATED' as ShipmentStatus,
};

/**
 * ManageShipments Page
 * Comprehensive interface for creating, updating, and managing shipments
 */
export function ManageShipments() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [currentTab, setCurrentTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(searchParams.get('action') === 'create');
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editShipment, setEditShipment] = useState(emptyEditShipment);
  const [page, setPage] = useState(1);

  // Fetch shipments with pagination
  const {
    data: shipmentsData,
    isLoading,
    error,
    refetch,
  } = useShipments(page, 20);

  const createShipmentMutation = useCreateShipment();
  const updateShipmentMutation = useUpdateShipment();
  const editStatusOptions = SHIPMENT_STATUS_OPTIONS.includes(editShipment.current_status)
    ? SHIPMENT_STATUS_OPTIONS
    : [editShipment.current_status, ...SHIPMENT_STATUS_OPTIONS];

  // Form state for creating shipment
  const [newShipment, setNewShipment] = useState({
    tracking_number: '',
    origin: '',
    destination: '',
    customer_id: '',
    current_location: '',
    current_status: 'PORT_RECEIVED' as ShipmentStatus,
  });

  const handleCreateShipment = async () => {
    try {
      await createShipmentMutation.mutateAsync(newShipment);
      setCreateDialogOpen(false);
      setNewShipment({
        tracking_number: '',
        origin: '',
        destination: '',
        customer_id: '',
        current_location: '',
        current_status: 'PORT_RECEIVED',
      });
      refetch();
    } catch (error) {
      console.error('Failed to create shipment:', error);
    }
  };

  const handleOpenEditDialog = (shipment: Shipment) => {
    setEditShipment({
      tracking_number: shipment.tracking_number,
      origin: shipment.origin,
      destination: shipment.destination,
      customer_id: shipment.customer_id || '',
      current_location: shipment.current_location || '',
      current_status: shipment.current_status as ShipmentStatus,
    });
    setEditDialogOpen(true);
  };

  const handleUpdateShipment = async () => {
    try {
      await updateShipmentMutation.mutateAsync({
        trackingNumber: editShipment.tracking_number,
        data: {
          origin: editShipment.origin,
          destination: editShipment.destination,
          customer_id: editShipment.customer_id || undefined,
          current_location: editShipment.current_location || undefined,
          current_status: editShipment.current_status,
        },
      });
      setEditDialogOpen(false);
      setEditShipment(emptyEditShipment);
      refetch();
    } catch (error) {
      console.error('Failed to update shipment:', error);
    }
  };

  const filteredShipments = shipmentsData?.items.filter((shipment) =>
    shipment.tracking_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
    shipment.origin.toLowerCase().includes(searchQuery.toLowerCase()) ||
    shipment.destination.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 3 }}>
      <Container maxWidth="xl">
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <IconButton onClick={() => navigate('/')} color="primary">
              <ArrowBackIcon />
            </IconButton>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h4" fontWeight={600}>
                Manage Shipments
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Create, update, and track all your shipments
              </Typography>
            </Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setCreateDialogOpen(true)}
              size="large"
            >
              Create Shipment
            </Button>
            <IconButton onClick={() => refetch()} color="primary">
              <RefreshIcon />
            </IconButton>
          </Box>

          {/* Search and Filter Bar */}
          <Paper sx={{ p: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  placeholder="Search by tracking number, origin, or destination..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  InputProps={{
                    startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                  <Button startIcon={<FilterIcon />} variant="outlined">
                    Filters
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Box>

        {/* Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
            <Tab label={`All Shipments (${shipmentsData?.total || 0})`} />
            <Tab label="Active" />
            <Tab label="Delivered" />
            <Tab label="With Alerts" />
          </Tabs>
        </Paper>

        {/* Content */}
        <Paper sx={{ p: 3 }}>
          {isLoading && <LoadingSpinner message="Loading shipments..." />}

          {error && (
            <MuiAlert severity="error" sx={{ mb: 2 }}>
              Failed to load shipments. Please try again.
            </MuiAlert>
          )}

          <TabPanel value={currentTab} index={0}>
            {!isLoading && !error && filteredShipments && filteredShipments.length > 0 && (
              <Grid container spacing={2}>
                {filteredShipments.map((shipment) => (
                  <Grid item xs={12} sm={6} md={4} key={shipment.id}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <ShipmentCard
                        shipment={shipment}
                        onClick={() => handleOpenEditDialog(shipment)}
                      />
                      <Button
                        variant="outlined"
                        startIcon={<EditIcon />}
                        onClick={() => handleOpenEditDialog(shipment)}
                        fullWidth
                      >
                        Edit Shipment
                      </Button>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            )}

            {!isLoading && !error && (!filteredShipments || filteredShipments.length === 0) && (
              <EmptyState
                title="No Shipments Found"
                description={
                  searchQuery
                    ? 'No shipments match your search criteria.'
                    : 'Create your first shipment to get started.'
                }
                action={
                  !searchQuery
                    ? {
                        label: 'Create Shipment',
                        onClick: () => setCreateDialogOpen(true),
                      }
                    : undefined
                }
              />
            )}

            {/* Pagination */}
            {shipmentsData && shipmentsData.total_pages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 4 }}>
                <Button
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                  variant="outlined"
                >
                  Previous
                </Button>
                <Typography sx={{ display: 'flex', alignItems: 'center', px: 2 }}>
                  Page {page} of {shipmentsData.total_pages}
                </Typography>
                <Button
                  disabled={page === shipmentsData.total_pages}
                  onClick={() => setPage(page + 1)}
                  variant="outlined"
                >
                  Next
                </Button>
              </Box>
            )}
          </TabPanel>

          <TabPanel value={currentTab} index={1}>
            <Typography>Active shipments view (to be implemented)</Typography>
          </TabPanel>

          <TabPanel value={currentTab} index={2}>
            <Typography>Delivered shipments view (to be implemented)</Typography>
          </TabPanel>

          <TabPanel value={currentTab} index={3}>
            <Typography>Shipments with alerts view (to be implemented)</Typography>
          </TabPanel>
        </Paper>

        {/* Create Shipment Dialog */}
        <Dialog
          open={createDialogOpen}
          onClose={() => setCreateDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Create New Shipment</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
              <TextField
                label="Tracking Number"
                value={newShipment.tracking_number}
                onChange={(e) => setNewShipment({ ...newShipment, tracking_number: e.target.value })}
                required
                fullWidth
              />
              <TextField
                label="Origin"
                value={newShipment.origin}
                onChange={(e) => setNewShipment({ ...newShipment, origin: e.target.value })}
                required
                fullWidth
              />
              <TextField
                label="Destination"
                value={newShipment.destination}
                onChange={(e) => setNewShipment({ ...newShipment, destination: e.target.value })}
                required
                fullWidth
              />
              <TextField
                label="Customer ID"
                value={newShipment.customer_id}
                onChange={(e) => setNewShipment({ ...newShipment, customer_id: e.target.value })}
                required
                fullWidth
              />
              <TextField
                label="Current Location"
                value={newShipment.current_location}
                onChange={(e) => setNewShipment({ ...newShipment, current_location: e.target.value })}
                required
                fullWidth
              />
              <FormControl fullWidth>
                <InputLabel>Initial Status</InputLabel>
                <Select
                  value={newShipment.current_status}
                  label="Initial Status"
                  onChange={(e) =>
                    setNewShipment({ ...newShipment, current_status: e.target.value as ShipmentStatus })
                  }
                >
                  <MenuItem value="PORT_RECEIVED">Port Received</MenuItem>
                  <MenuItem value="CUSTOMS_SUBMITTED">Customs Submitted</MenuItem>
                  <MenuItem value="CUSTOMS_CLEARED">Customs Cleared</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleCreateShipment}
              variant="contained"
              disabled={
                !newShipment.tracking_number ||
                !newShipment.origin ||
                !newShipment.destination ||
                !newShipment.customer_id ||
                createShipmentMutation.isPending
              }
            >
              {createShipmentMutation.isPending ? 'Creating...' : 'Create Shipment'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Edit Shipment Dialog */}
        <Dialog
          open={editDialogOpen}
          onClose={() => setEditDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Update Shipment</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
              <TextField
                label="Tracking Number"
                value={editShipment.tracking_number}
                disabled
                fullWidth
              />
              <TextField
                label="Origin"
                value={editShipment.origin}
                onChange={(e) => setEditShipment({ ...editShipment, origin: e.target.value })}
                required
                fullWidth
              />
              <TextField
                label="Destination"
                value={editShipment.destination}
                onChange={(e) => setEditShipment({ ...editShipment, destination: e.target.value })}
                required
                fullWidth
              />
              <TextField
                label="Customer ID"
                value={editShipment.customer_id}
                onChange={(e) => setEditShipment({ ...editShipment, customer_id: e.target.value })}
                fullWidth
              />
              <TextField
                label="Current Location"
                value={editShipment.current_location}
                onChange={(e) => setEditShipment({ ...editShipment, current_location: e.target.value })}
                fullWidth
              />
              <FormControl fullWidth>
                <InputLabel>Current Status</InputLabel>
                <Select
                  value={editShipment.current_status}
                  label="Current Status"
                  onChange={(e) =>
                    setEditShipment({ ...editShipment, current_status: e.target.value as ShipmentStatus })
                  }
                >
                  {editStatusOptions.map((status) => (
                    <MenuItem key={status} value={status}>
                      {formatStatusLabel(status)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleUpdateShipment}
              variant="contained"
              disabled={
                !editShipment.origin ||
                !editShipment.destination ||
                updateShipmentMutation.isPending
              }
            >
              {updateShipmentMutation.isPending ? 'Updating...' : 'Update Shipment'}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}

// Made with Bob
