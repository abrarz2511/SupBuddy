# SupBuddy Frontend - React Dashboard

A modern React dashboard for real-time logistics tracking with AI-powered exception analysis.

## 🚀 Quick Start

### Prerequisites

- **Node.js**: v18+ or v20+ (recommended)
- **npm**: v9+ or v10+
- **Backend API**: Running on `http://localhost:8000` (see Backend README)

### Installation

1. **Navigate to Frontend directory:**
   ```bash
   cd Frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   # .env file is already created with defaults
   # Edit if you need to change API URL or other settings
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

5. **Open in browser:**
   ```
   http://localhost:3000
   ```

## 📦 What's Included

### ✅ Completed Features

- **TypeScript Configuration** - Full type safety with strict mode
- **API Client Layer** - Axios-based REST client with:
  - Automatic error handling and retry logic
  - Request/response interceptors
  - Token-based authentication support
  - Development logging
- **Type Definitions** - Complete types for:
  - Shipments, Milestones, Schedules
  - Alerts, Analysis, Priorities
  - API responses and errors
- **Material-UI Theme** - Custom theme with:
  - Color palette for alert priorities
  - Typography system
  - Component overrides
- **React Query Setup** - Server state management configured
- **Environment Configuration** - Centralized config with .env support

### 🚧 In Progress

- Dashboard layout components
- Shipments widget
- Alerts widget with filtering
- AI analysis panel
- Data visualization charts

## 📁 Project Structure

```
Frontend/
├── public/                 # Static assets
├── src/
│   ├── api/               # API service layer
│   │   ├── client.ts      # Axios instance
│   │   ├── shipments.ts   # Shipments API
│   │   ├── alerts.ts      # Alerts API
│   │   └── schedules.ts   # Schedules API
│   ├── components/        # React components (to be added)
│   ├── config/            # Configuration
│   │   └── api.config.ts  # API settings
│   ├── hooks/             # Custom React hooks (to be added)
│   ├── theme/             # MUI theme
│   │   └── theme.ts       # Theme configuration
│   ├── types/             # TypeScript types
│   │   ├── shipment.ts    # Shipment types
│   │   ├── alert.ts       # Alert types
│   │   └── api.ts         # API types
│   ├── App.tsx            # Root component
│   ├── main.tsx           # Entry point
│   └── vite-env.d.ts      # Vite types
├── .env                   # Environment variables
├── .env.example           # Environment template
├── index.html             # HTML template
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── vite.config.ts         # Vite config
└── README.md              # This file
```

## 🔧 Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## 🌐 API Integration

### Backend Endpoints

The frontend connects to these backend endpoints:

- `GET /api/v1/shipments` - List shipments
- `GET /api/v1/shipments/{tracking_number}` - Get shipment details
- `GET /api/v1/alerts` - List alerts
- `GET /api/v1/alerts/{alert_id}` - Get alert with AI analysis
- `POST /api/v1/alerts/{alert_id}/analyze` - Trigger AI analysis
- `PUT /api/v1/alerts/{alert_id}/resolve` - Resolve alert
- `GET /api/v1/schedules/{shipment_id}` - Get shipment schedule

### API Configuration

Edit `.env` to configure API settings:

```env
# API Base URL
VITE_API_BASE_URL=http://localhost:8000

# Request timeout (ms)
VITE_API_TIMEOUT=30000

# Auto-refresh interval (ms)
VITE_REFRESH_INTERVAL=30000

# Enable/disable features
VITE_ENABLE_AUTO_REFRESH=true
VITE_ENABLE_WEBSOCKET=false
```

## 🎨 UI Components (Planned)

### Dashboard Layout
- Header with navigation and user menu
- Stats cards showing key metrics
- Grid layout for widgets

### Shipments Widget
- List of active shipments
- Status indicators with colors
- Timeline view of milestones
- Click to view details

### Alerts Widget
- Filterable alert list
- Priority-based color coding:
  - 🔴 CRITICAL (Red)
  - 🟠 HIGH (Orange)
  - 🟡 MEDIUM (Yellow)
  - 🔵 LOW (Blue)
- Status badges
- Click to view AI analysis

### AI Analysis Panel
- Likely cause explanation
- Risk priority assessment
- Confidence score meter
- Supporting evidence cards
- External factors (weather, traffic, etc.)
- Recommended actions

### Charts & Visualizations
- Alert trends over time (line chart)
- Priority distribution (donut chart)
- Shipment status breakdown (bar chart)

## 🔐 Authentication (Future)

Currently, the API client supports token-based authentication:

```typescript
// Token is stored in localStorage
localStorage.setItem('auth_token', 'your_token_here');

// Automatically added to requests via interceptor
```

## 🐛 Troubleshooting

### TypeScript Errors

The TypeScript errors you see are expected until dependencies are installed:

```bash
npm install
```

### Port Already in Use

If port 3000 is in use, Vite will automatically try the next available port (3001, 3002, etc.).

### API Connection Issues

1. Ensure backend is running on `http://localhost:8000`
2. Check CORS settings in backend
3. Verify `.env` has correct `VITE_API_BASE_URL`

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

## 📚 Technology Stack

- **React 18** - UI library
- **TypeScript 5** - Type safety
- **Vite 5** - Build tool
- **Material-UI 5** - Component library
- **React Query 5** - Server state management
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **React Router 6** - Navigation (to be added)

## 🎯 Development Workflow

1. **Start Backend**: Ensure backend API is running
2. **Start Frontend**: Run `npm run dev`
3. **Make Changes**: Edit files in `src/`
4. **Hot Reload**: Changes appear instantly
5. **Check Types**: TypeScript validates on save
6. **Test API**: Use browser DevTools Network tab

## 📖 Next Steps

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Verify Backend Connection**:
   - Start backend: `cd Backend && uvicorn main:app --reload`
   - Check http://localhost:8000/docs

3. **Start Development**:
   ```bash
   npm run dev
   ```

4. **Build Dashboard Components**:
   - Create layout components
   - Add shipments widget
   - Add alerts widget
   - Implement AI analysis panel

## 🤝 Contributing

When adding new features:

1. Create types in `src/types/`
2. Add API calls in `src/api/`
3. Create components in `src/components/`
4. Add hooks in `src/hooks/`
5. Update this README

## 📄 License

Part of the SupBuddy logistics tracking system.

---

**Status**: ✅ Foundation Complete | 🚧 UI Components In Progress

For backend documentation, see `Backend/README.md`