# SupBuddy Dashboard - Implementation Guide

## Overview

The SupBuddy Dashboard is a comprehensive React-based interface for monitoring logistics shipments, tracking alerts, and managing shipments with AI-powered exception analysis.

## Features Implemented

### 1. **Dashboard Page** (`/`)
The main dashboard provides a real-time overview of your logistics operations:

#### Three Main Sections:
1. **Active Shipments (Left Column)**
   - Displays up to 10 active shipments in a kanban-style card layout
   - Each shipment card shows:
     - Tracking number
     - Current status with color-coded badge
     - Current location
     - Origin → Destination route
     - Progress bar based on shipment stage
     - Alert indicators (if any)
     - Last update timestamp
   - Click "View All Shipments" button to navigate to manage shipments page
   - Auto-refreshes every 30 seconds

2. **Active Alerts (Right Column)**
   - Shows up to 5 most recent active alerts
   - Each alert card displays:
     - Priority badge (CRITICAL, HIGH, MEDIUM, LOW)
     - Status badge (OPEN, ANALYZING, ANALYZED, RESOLVED, CLOSED)
     - Alert type and description
     - Associated shipment tracking number
     - Delay information (if applicable)
     - AI analysis availability indicator
     - Detection timestamp
   - Click "View All Alerts" to see complete list
   - Auto-refreshes every 30 seconds

3. **Quick Actions (Right Column, Top)**
   - **Create New Shipment**: Opens dialog to create a new shipment
   - **Manage Shipments**: Navigates to the comprehensive shipment management page

### 2. **Manage Shipments Page** (`/manage-shipments`)
A comprehensive interface for managing all shipments:

#### Features:
- **Search Functionality**: Search by tracking number, origin, or destination
- **Pagination**: Navigate through large shipment lists (20 per page)
- **Tabbed Interface**:
  - All Shipments
  - Active Shipments
  - Delivered Shipments
  - Shipments with Alerts
- **Create Shipment Dialog**: Form to create new shipments with:
  - Tracking number
  - Origin and destination
  - Customer ID
  - Current location
  - Initial status
- **Grid Layout**: Responsive grid showing shipment cards
- **Back Navigation**: Easy return to dashboard

### 3. **Reusable Components**

#### ShipmentCard
- Kanban-style card for displaying shipment information
- Color-coded status indicator
- Progress bar showing shipment stage
- Alert badge for shipments with issues
- Clickable for detailed view

#### AlertCard
- Displays alert information with priority and status
- Shows AI analysis availability
- Includes delay information
- Links to associated shipment

#### StatusBadge
- Reusable badge component for:
  - Shipment statuses
  - Alert priorities
  - Alert statuses
- Color-coded for quick visual identification

#### LoadingSpinner
- Consistent loading indicator across the app
- Customizable message and size

#### EmptyState
- User-friendly empty state component
- Customizable icon, title, description
- Optional action button

## Technical Architecture

### State Management
- **React Query (TanStack Query)**: Server state management
  - Automatic caching and background refetching
  - Optimistic updates
  - Error handling
  - Auto-refresh every 30 seconds

### API Integration
- **Custom Hooks**:
  - `useActiveShipments()`: Fetch active shipments
  - `useShipments(page, pageSize)`: Paginated shipment list
  - `useActiveAlerts()`: Fetch active alerts
  - `useCreateShipment()`: Create new shipment mutation
  - `useAddMilestone()`: Add milestone to shipment
  - `useAnalyzeAlert()`: Trigger AI analysis

### Routing
- **React Router v6**: Client-side routing
  - `/` - Dashboard
  - `/manage-shipments` - Shipment management
  - Query parameters supported (e.g., `?action=create`)

### Responsive Design
- **Material-UI Grid System**: Responsive breakpoints
  - Mobile (xs): Single column layout
  - Tablet (sm, md): Adjusted columns
  - Desktop (lg, xl): Full three-column layout
- **Flexible Components**: All components adapt to screen size

## Data Flow

```
User Action → Component → Custom Hook → API Client → Backend API
                ↓
         React Query Cache
                ↓
         Component Re-render
```

## Key Features

### Auto-Refresh
- Dashboard automatically refreshes data every 30 seconds
- Manual refresh button available
- Stale time configured to prevent excessive requests

### Navigation Flow
1. **Dashboard** → View overview
2. **Click "Manage Shipments"** → Full shipment management
3. **Click "Create Shipment"** → Create new shipment dialog
4. **Click Shipment Card** → Detailed shipment view (to be implemented)
5. **Click Alert Card** → Detailed alert analysis (to be implemented)

### Pagination
- Manage Shipments page supports pagination
- 20 shipments per page
- Previous/Next navigation
- Page indicator

### Search & Filter
- Real-time search in Manage Shipments
- Filters by tracking number, origin, destination
- Additional filter options available

## Component Structure

```
Frontend/src/
├── pages/
│   ├── Dashboard.tsx          # Main dashboard page
│   └── ManageShipments.tsx    # Shipment management page
├── components/
│   ├── common/
│   │   ├── StatusBadge.tsx    # Status indicator
│   │   ├── LoadingSpinner.tsx # Loading state
│   │   └── EmptyState.tsx     # Empty state
│   ├── shipments/
│   │   └── ShipmentCard.tsx   # Shipment card
│   └── alerts/
│       └── AlertCard.tsx      # Alert card
├── hooks/
│   ├── useShipments.ts        # Shipment data hooks
│   └── useAlerts.ts           # Alert data hooks
├── api/
│   ├── shipments.ts           # Shipment API calls
│   └── alerts.ts              # Alert API calls
└── types/
    ├── shipment.ts            # Shipment types
    └── alert.ts               # Alert types
```

## Usage

### Starting the Application

```bash
cd Frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`

### Environment Variables

Create a `.env` file in the Frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Creating a Shipment

1. Navigate to Dashboard
2. Click "Create New Shipment" or go to Manage Shipments
3. Fill in the form:
   - Tracking Number (required)
   - Origin (required)
   - Destination (required)
   - Customer ID (required)
   - Current Location (required)
   - Initial Status (default: Port Received)
4. Click "Create Shipment"

### Viewing Shipments

- **Dashboard**: See up to 10 most recent active shipments
- **Manage Shipments**: View all shipments with pagination and search

### Monitoring Alerts

- **Dashboard**: See up to 5 most recent active alerts
- Click on alert card for detailed analysis (to be implemented)

## Responsive Behavior

### Mobile (< 600px)
- Single column layout
- Stacked sections
- Full-width cards
- Simplified navigation

### Tablet (600px - 960px)
- Two-column grid for shipment cards
- Stacked main sections
- Optimized spacing

### Desktop (> 960px)
- Three-column layout on dashboard
- Three-column grid for shipment cards
- Side-by-side sections
- Full feature set

## Color Coding

### Shipment Statuses
- **Port Received**: Blue (#2196f3)
- **Customs Submitted**: Orange (#ff9800)
- **Customs Cleared**: Green (#4caf50)
- **Delivery Center**: Purple (#9c27b0)
- **Regional Hub**: Cyan (#00bcd4)
- **Out for Delivery**: Deep Orange (#ff5722)
- **Delivered**: Green (#4caf50)

### Alert Priorities
- **CRITICAL**: Red background (#ffebee), Red text (#d32f2f)
- **HIGH**: Orange background (#fff3e0), Orange text (#f57c00)
- **MEDIUM**: Yellow background (#fffde7), Yellow text (#fbc02d)
- **LOW**: Blue background (#e3f2fd), Blue text (#1976d2)

### Alert Statuses
- **OPEN**: Red (#f44336)
- **ANALYZING**: Orange (#ff9800)
- **ANALYZED**: Blue (#2196f3)
- **RESOLVED**: Green (#4caf50)
- **CLOSED**: Grey (#9e9e9e)

## Future Enhancements

1. **Detailed Views**
   - Shipment detail page with full timeline
   - Alert detail page with complete AI analysis

2. **Advanced Filtering**
   - Date range filters
   - Multi-select status filters
   - Saved filter presets

3. **Real-time Updates**
   - WebSocket integration for live updates
   - Push notifications

4. **Analytics**
   - Charts and graphs
   - Performance metrics
   - SLA compliance reports

5. **Export Functionality**
   - Export shipments to CSV/Excel
   - Generate PDF reports

## Troubleshooting

### Shipments Not Loading
- Check backend API is running
- Verify `VITE_API_BASE_URL` in `.env`
- Check browser console for errors

### Auto-refresh Not Working
- React Query is configured with 30-second intervals
- Check network tab for API calls
- Verify no errors in console

### Navigation Issues
- Ensure React Router is properly configured
- Check for console errors
- Verify all routes are defined in App.tsx

## Made with Bob 🤖

This dashboard was built with careful attention to user experience, performance, and maintainability. All components are fully typed with TypeScript and follow React best practices.