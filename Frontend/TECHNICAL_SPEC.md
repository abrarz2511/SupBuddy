# SupBuddy Frontend - Technical Specification

## Overview

A React-based dashboard for monitoring logistics shipments, tracking alerts, and viewing AI-powered exception analysis. The dashboard provides real-time visibility into shipment status and proactive issue management.

---

## Technology Stack

### Core Framework
- **React 18.x** with TypeScript
- **Vite** for fast development and optimized builds
- **React Router v6** for navigation

### UI Framework
- **Material-UI (MUI) v5** for component library
- **MUI X Data Grid** for advanced tables
- **Recharts** for data visualization
- **MUI Icons** for iconography

### State Management
- **React Query (TanStack Query)** for server state management
- **Zustand** for lightweight client state (optional)
- **React Context** for theme and user preferences

### API Communication
- **Axios** for HTTP requests
- **Axios Interceptors** for error handling and auth

### Development Tools
- **ESLint** for code quality
- **Prettier** for code formatting
- **TypeScript** for type safety

---

## Project Structure

```
Frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/
│   │   ├── client.ts              # Axios instance configuration
│   │   ├── shipments.ts           # Shipment API calls
│   │   ├── alerts.ts              # Alert API calls
│   │   └── schedules.ts           # Schedule API calls
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx      # Main layout wrapper
│   │   │   ├── Header.tsx         # Top navigation bar
│   │   │   └── Sidebar.tsx        # Side navigation (optional)
│   │   ├── dashboard/
│   │   │   ├── DashboardGrid.tsx  # Main dashboard layout
│   │   │   ├── StatsCards.tsx     # Summary statistics
│   │   │   └── RefreshControl.tsx # Auto-refresh toggle
│   │   ├── shipments/
│   │   │   ├── ShipmentsWidget.tsx      # Active shipments list
│   │   │   ├── ShipmentCard.tsx         # Individual shipment card
│   │   │   ├── ShipmentTimeline.tsx     # Milestone timeline
│   │   │   └── ShipmentDetailsModal.tsx # Detailed view modal
│   │   ├── alerts/
│   │   │   ├── AlertsWidget.tsx         # Active alerts list
│   │   │   ├── AlertCard.tsx            # Individual alert card
│   │   │   ├── AlertFilters.tsx         # Filter controls
│   │   │   └── AlertDetailsModal.tsx    # Detailed alert view
│   │   ├── analysis/
│   │   │   ├── AnalysisPanel.tsx        # AI analysis display
│   │   │   ├── RiskIndicator.tsx        # Risk level visualization
│   │   │   ├── ConfidenceScore.tsx      # Confidence meter
│   │   │   └── EvidenceList.tsx         # Supporting evidence
│   │   ├── charts/
│   │   │   ├── AlertTrendChart.tsx      # Alert trends over time
│   │   │   ├── PriorityDistribution.tsx # Alert priority breakdown
│   │   │   └── ShipmentStatusChart.tsx  # Shipment status pie chart
│   │   └── common/
│   │       ├── LoadingSpinner.tsx       # Loading indicator
│   │       ├── ErrorBoundary.tsx        # Error handling
│   │       ├── EmptyState.tsx           # No data placeholder
│   │       └── StatusBadge.tsx          # Status indicator
│   ├── hooks/
│   │   ├── useShipments.ts        # Shipment data hook
│   │   ├── useAlerts.ts           # Alert data hook
│   │   ├── useAutoRefresh.ts      # Auto-refresh logic
│   │   └── useFilters.ts          # Filter state management
│   ├── types/
│   │   ├── shipment.ts            # Shipment type definitions
│   │   ├── alert.ts               # Alert type definitions
│   │   ├── analysis.ts            # Analysis type definitions
│   │   └── api.ts                 # API response types
│   ├── utils/
│   │   ├── formatters.ts          # Date/time formatters
│   │   ├── constants.ts           # App constants
│   │   └── helpers.ts             # Utility functions
│   ├── config/
│   │   └── api.config.ts          # API configuration
│   ├── theme/
│   │   └── theme.ts               # MUI theme customization
│   ├── pages/
│   │   ├── Dashboard.tsx          # Main dashboard page
│   │   ├── ShipmentDetails.tsx    # Shipment detail page
│   │   └── AlertDetails.tsx       # Alert detail page
│   ├── App.tsx                    # Root component
│   ├── main.tsx                   # Entry point
│   └── vite-env.d.ts              # Vite type definitions
├── .env.example                   # Environment variables template
├── .eslintrc.json                 # ESLint configuration
├── .prettierrc                    # Prettier configuration
├── tsconfig.json                  # TypeScript configuration
├── vite.config.ts                 # Vite configuration
├── package.json                   # Dependencies
└── README.md                      # Setup instructions
```

---

## Data Models

### Shipment Type
```typescript
interface Shipment {
  id: string;
  tracking_number: string;
  current_status: ShipmentStatus;
  current_location: string;
  origin: string;
  destination: string;
  customer_id: string;
  created_at: string;
  updated_at: string;
  milestones: Milestone[];
  schedules: Schedule[];
}

type ShipmentStatus = 
  | 'PORT_RECEIVED'
  | 'CUSTOMS_SUBMITTED'
  | 'CUSTOMS_CLEARED'
  | 'DELIVERY_CENTER_RECEIVED'
  | 'REGIONAL_HUB_RECEIVED'
  | 'OUT_FOR_DELIVERY'
  | 'DELIVERED';

interface Milestone {
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
```

### Alert Type
```typescript
interface Alert {
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

type AlertType = 
  | 'MISSING_UPDATE'
  | 'LATE_ARRIVAL'
  | 'STALE_STATUS'
  | 'CUSTOMS_DELAY'
  | 'LOCATION_MISMATCH';

type AlertPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

type AlertStatus = 
  | 'OPEN'
  | 'ANALYZING'
  | 'ANALYZED'
  | 'RESOLVED'
  | 'CLOSED';
```

### Analysis Type
```typescript
interface AlertAnalysis {
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
```

---

## API Integration

### Base Configuration
```typescript
// config/api.config.ts
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  refreshInterval: 30000, // 30 seconds
};
```

### API Service Layer

#### Shipments API
```typescript
// api/shipments.ts
export const shipmentsApi = {
  getAll: (params?: ShipmentQueryParams) => 
    axios.get<Shipment[]>('/api/v1/shipments', { params }),
  
  getByTrackingNumber: (trackingNumber: string) =>
    axios.get<Shipment>(`/api/v1/shipments/${trackingNumber}`),
  
  getActiveShipments: () =>
    axios.get<Shipment[]>('/api/v1/shipments', {
      params: { status: 'active', limit: 50 }
    }),
};
```

#### Alerts API
```typescript
// api/alerts.ts
export const alertsApi = {
  getAll: (params?: AlertQueryParams) =>
    axios.get<Alert[]>('/api/v1/alerts', { params }),
  
  getById: (alertId: string) =>
    axios.get<AlertWithAnalysis>(`/api/v1/alerts/${alertId}`),
  
  getActiveAlerts: () =>
    axios.get<Alert[]>('/api/v1/alerts', {
      params: { status: 'OPEN,ANALYZING,ANALYZED', limit: 100 }
    }),
  
  triggerAnalysis: (alertId: string) =>
    axios.post(`/api/v1/alerts/${alertId}/analyze`),
  
  resolve: (alertId: string, notes: string) =>
    axios.put(`/api/v1/alerts/${alertId}/resolve`, {
      resolution_notes: notes
    }),
};
```

---

## Component Specifications

### 1. Dashboard Layout

**DashboardGrid.tsx**
- Grid layout using MUI Grid system
- Responsive breakpoints (xs, sm, md, lg, xl)
- Three main sections:
  - Stats cards (top row)
  - Active shipments (left column)
  - Active alerts + Analysis (right column)

**Layout Structure:**
```
┌─────────────────────────────────────────────┐
│  Header (App Title, Refresh, User Menu)    │
├─────────────────────────────────────────────┤
│  Stats Cards (Total, Active, Critical)     │
├──────────────────────┬──────────────────────┤
│                      │                      │
│  Active Shipments    │  Active Alerts       │
│  (Scrollable List)   │  (Filterable List)   │
│                      │                      │
│                      ├──────────────────────┤
│                      │                      │
│                      │  AI Analysis Panel   │
│                      │  (Selected Alert)    │
│                      │                      │
└──────────────────────┴──────────────────────┘
```

### 2. Active Shipments Widget

**Features:**
- Display 10-20 most recent active shipments
- Show tracking number, current status, location
- Color-coded status indicators
- Click to view detailed timeline
- Auto-refresh every 30 seconds

**Visual Design:**
- Card-based layout
- Status badge with icon
- Progress indicator showing milestone completion
- Last update timestamp

### 3. Active Alerts Widget

**Features:**
- List all open/analyzing/analyzed alerts
- Filter by priority (CRITICAL, HIGH, MEDIUM, LOW)
- Filter by status (OPEN, ANALYZING, ANALYZED)
- Sort by detected time, priority
- Color-coded priority badges
- Click to view analysis

**Visual Design:**
- Table or card list view
- Priority color coding:
  - CRITICAL: Red (#d32f2f)
  - HIGH: Orange (#f57c00)
  - MEDIUM: Yellow (#fbc02d)
  - LOW: Blue (#1976d2)
- Alert type icon
- Delay time display
- Analysis status indicator

### 4. AI Analysis Panel

**Features:**
- Display AI agent analysis for selected alert
- Show likely cause with confidence score
- Risk priority assessment
- Supporting evidence from external sources
- Recommended actions
- Confidence meter visualization

**Visual Design:**
- Expandable/collapsible sections
- Confidence score as circular progress
- Evidence cards with icons
- Risk level indicator
- Action buttons (Resolve, Escalate)

### 5. Charts & Visualizations

**Alert Trend Chart:**
- Line chart showing alerts over time (last 7 days)
- Grouped by priority level
- Interactive tooltips

**Priority Distribution:**
- Donut chart showing alert breakdown by priority
- Percentage labels
- Click to filter

**Shipment Status Chart:**
- Horizontal bar chart showing shipments by status
- Count labels
- Color-coded by status

---

## State Management Strategy

### React Query for Server State
```typescript
// hooks/useAlerts.ts
export function useAlerts(filters?: AlertFilters) {
  return useQuery({
    queryKey: ['alerts', filters],
    queryFn: () => alertsApi.getAll(filters),
    refetchInterval: API_CONFIG.refreshInterval,
    staleTime: 20000,
  });
}

// hooks/useShipments.ts
export function useShipments() {
  return useQuery({
    queryKey: ['shipments', 'active'],
    queryFn: () => shipmentsApi.getActiveShipments(),
    refetchInterval: API_CONFIG.refreshInterval,
  });
}
```

### Local State for UI
- Filter selections (priority, status, date range)
- Selected alert/shipment for detail view
- Auto-refresh toggle state
- Modal open/close state

---

## Key Features Implementation

### 1. Auto-Refresh
```typescript
// hooks/useAutoRefresh.ts
export function useAutoRefresh(enabled: boolean, interval: number) {
  const queryClient = useQueryClient();
  
  useEffect(() => {
    if (!enabled) return;
    
    const timer = setInterval(() => {
      queryClient.invalidateQueries(['alerts']);
      queryClient.invalidateQueries(['shipments']);
    }, interval);
    
    return () => clearInterval(timer);
  }, [enabled, interval, queryClient]);
}
```

### 2. Real-time Updates
- Use React Query's `refetchInterval` for polling
- Optional: WebSocket integration for push updates (future)
- Visual indicator when data is refreshing

### 3. Error Handling
```typescript
// components/common/ErrorBoundary.tsx
- Catch and display API errors gracefully
- Retry mechanism for failed requests
- Fallback UI for error states
```

### 4. Loading States
- Skeleton loaders for initial load
- Spinner for refresh operations
- Progress indicators for long operations

### 5. Responsive Design
- Mobile-first approach
- Breakpoints:
  - xs: 0-600px (mobile)
  - sm: 600-960px (tablet)
  - md: 960-1280px (small desktop)
  - lg: 1280-1920px (desktop)
  - xl: 1920px+ (large desktop)

---

## Performance Optimizations

1. **Code Splitting**
   - Lazy load detail pages
   - Dynamic imports for charts

2. **Memoization**
   - Use `React.memo` for expensive components
   - `useMemo` for computed values
   - `useCallback` for event handlers

3. **Virtual Scrolling**
   - Implement for long lists (100+ items)
   - Use `react-window` or MUI Data Grid virtualization

4. **Image Optimization**
   - Lazy load images
   - Use appropriate formats (WebP)

5. **Bundle Size**
   - Tree-shaking unused code
   - Analyze bundle with `vite-bundle-visualizer`

---

## Testing Strategy

### Unit Tests
- Component rendering tests
- Hook logic tests
- Utility function tests

### Integration Tests
- API integration tests
- User flow tests
- Filter and sort functionality

### E2E Tests (Optional)
- Critical user journeys
- Dashboard load and interaction

---

## Deployment Considerations

### Environment Variables
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_REFRESH_INTERVAL=30000
VITE_ENABLE_ANALYTICS=false
```

### Build Configuration
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'mui-vendor': ['@mui/material', '@mui/icons-material'],
          'charts': ['recharts'],
        },
      },
    },
  },
});
```

### CORS Configuration
- Backend must allow frontend origin
- Handle preflight requests
- Set appropriate headers

---

## Future Enhancements

1. **WebSocket Integration**
   - Real-time push notifications
   - Live alert updates

2. **Advanced Filtering**
   - Date range picker
   - Multi-select filters
   - Saved filter presets

3. **Export Functionality**
   - Export alerts to CSV/Excel
   - Generate PDF reports

4. **User Preferences**
   - Customizable dashboard layout
   - Theme selection (light/dark)
   - Notification preferences

5. **Mobile App**
   - React Native version
   - Push notifications

6. **Analytics Dashboard**
   - Historical trends
   - Performance metrics
   - SLA compliance reports

---

## Dependencies

### Core Dependencies
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "@mui/material": "^5.14.0",
  "@mui/icons-material": "^5.14.0",
  "@mui/x-data-grid": "^6.18.0",
  "@tanstack/react-query": "^5.0.0",
  "axios": "^1.6.0",
  "recharts": "^2.10.0",
  "date-fns": "^2.30.0"
}
```

### Dev Dependencies
```json
{
  "@types/react": "^18.2.0",
  "@types/react-dom": "^18.2.0",
  "@vitejs/plugin-react": "^4.2.0",
  "typescript": "^5.3.0",
  "vite": "^5.0.0",
  "eslint": "^8.55.0",
  "prettier": "^3.1.0"
}
```

---

## Timeline Estimate

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Setup | Project initialization, dependencies, configuration | 2-3 hours |
| API Layer | API client, service functions, types | 3-4 hours |
| Core Components | Layout, common components, hooks | 4-6 hours |
| Dashboard | Main dashboard, stats, widgets | 6-8 hours |
| Alerts | Alert list, filters, detail view | 4-6 hours |
| Analysis | AI analysis panel, visualizations | 4-5 hours |
| Charts | Data visualization components | 3-4 hours |
| Polish | Error handling, loading states, responsive design | 4-6 hours |
| Testing | Unit tests, integration tests | 4-6 hours |
| Documentation | README, comments, deployment guide | 2-3 hours |
| **Total** | | **36-51 hours** |

---

## Success Criteria

✅ Dashboard loads and displays active shipments and alerts
✅ Real-time data updates every 30 seconds
✅ Alert filtering by priority and status works correctly
✅ AI analysis displays with confidence scores and evidence
✅ Responsive design works on mobile, tablet, and desktop
✅ Error states handled gracefully with retry options
✅ Loading states provide clear feedback
✅ Charts visualize data trends effectively
✅ Navigation between views is smooth and intuitive
✅ Code is well-typed with TypeScript
✅ Components are reusable and maintainable

---

## Next Steps

1. Review and approve this specification
2. Set up development environment
3. Initialize React project with Vite
4. Install dependencies
5. Begin implementation following the todo list
6. Iterate based on feedback
