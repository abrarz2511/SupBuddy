# SupBuddy Frontend - Architecture Overview

## System Architecture

```mermaid
graph TB
    subgraph "Frontend Application"
        UI[React UI Components]
        Router[React Router]
        Query[React Query Cache]
        API[API Service Layer]
    end
    
    subgraph "Backend API"
        FastAPI[FastAPI Server]
        DB[(PostgreSQL)]
        Agent[Watsonx AI Agent]
    end
    
    UI --> Router
    UI --> Query
    Query --> API
    API --> FastAPI
    FastAPI --> DB
    FastAPI --> Agent
    
    style UI fill:#61dafb
    style Query fill:#ff4154
    style API fill:#00d8ff
    style FastAPI fill:#009688
```

## Component Hierarchy

```mermaid
graph TD
    App[App.tsx]
    App --> Layout[AppLayout]
    App --> Router[React Router]
    
    Router --> Dashboard[Dashboard Page]
    Router --> ShipmentDetail[Shipment Detail Page]
    Router --> AlertDetail[Alert Detail Page]
    
    Layout --> Header[Header]
    Layout --> Content[Main Content]
    
    Dashboard --> Stats[Stats Cards]
    Dashboard --> ShipmentsWidget[Shipments Widget]
    Dashboard --> AlertsWidget[Alerts Widget]
    Dashboard --> AnalysisPanel[Analysis Panel]
    Dashboard --> Charts[Charts Section]
    
    ShipmentsWidget --> ShipmentCard[Shipment Card]
    ShipmentCard --> Timeline[Timeline]
    
    AlertsWidget --> AlertFilters[Alert Filters]
    AlertsWidget --> AlertCard[Alert Card]
    
    AnalysisPanel --> RiskIndicator[Risk Indicator]
    AnalysisPanel --> ConfidenceScore[Confidence Score]
    AnalysisPanel --> EvidenceList[Evidence List]
    
    Charts --> TrendChart[Alert Trend Chart]
    Charts --> PriorityChart[Priority Distribution]
    Charts --> StatusChart[Status Chart]
    
    style App fill:#61dafb
    style Dashboard fill:#4caf50
    style ShipmentsWidget fill:#2196f3
    style AlertsWidget fill:#ff9800
    style AnalysisPanel fill:#9c27b0
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as React Components
    participant RQ as React Query
    participant API as API Service
    participant Backend as FastAPI Backend
    
    User->>UI: Load Dashboard
    UI->>RQ: useAlerts() hook
    RQ->>API: alertsApi.getActiveAlerts()
    API->>Backend: GET /api/v1/alerts
    Backend-->>API: Alert data + Analysis
    API-->>RQ: Parsed response
    RQ-->>UI: Cached data
    UI-->>User: Render alerts
    
    Note over RQ: Auto-refresh every 30s
    
    User->>UI: Click alert
    UI->>RQ: useAlertDetails(id)
    RQ->>API: alertsApi.getById(id)
    API->>Backend: GET /api/v1/alerts/{id}
    Backend-->>API: Detailed alert + AI analysis
    API-->>RQ: Parsed response
    RQ-->>UI: Cached data
    UI-->>User: Show analysis panel
```

## State Management

```mermaid
graph LR
    subgraph "Server State - React Query"
        Alerts[Alerts Cache]
        Shipments[Shipments Cache]
        Analysis[Analysis Cache]
    end
    
    subgraph "Client State - React Context/Hooks"
        Filters[Filter State]
        UI[UI State]
        Prefs[User Preferences]
    end
    
    subgraph "Components"
        Dashboard[Dashboard]
        Widgets[Widgets]
    end
    
    Dashboard --> Alerts
    Dashboard --> Shipments
    Dashboard --> Filters
    Dashboard --> UI
    
    Widgets --> Alerts
    Widgets --> Shipments
    Widgets --> Analysis
    Widgets --> Filters
    
    style Alerts fill:#ff4154
    style Shipments fill:#ff4154
    style Analysis fill:#ff4154
    style Filters fill:#4caf50
    style UI fill:#4caf50
```

## API Integration Pattern

```mermaid
graph TB
    subgraph "API Layer Structure"
        Client[Axios Client Instance]
        
        Client --> Shipments[Shipments API]
        Client --> Alerts[Alerts API]
        Client --> Schedules[Schedules API]
        
        Shipments --> GetAll[getAll]
        Shipments --> GetOne[getByTrackingNumber]
        Shipments --> GetActive[getActiveShipments]
        
        Alerts --> AGetAll[getAll]
        Alerts --> AGetOne[getById]
        Alerts --> AGetActive[getActiveAlerts]
        Alerts --> Analyze[triggerAnalysis]
        Alerts --> Resolve[resolve]
        
        Schedules --> SGet[getByShipmentId]
    end
    
    subgraph "Configuration"
        Config[api.config.ts]
        Env[.env variables]
    end
    
    Config --> Client
    Env --> Config
    
    style Client fill:#00d8ff
    style Config fill:#ffc107
```

## Component Communication

```mermaid
graph TB
    subgraph "Dashboard Container"
        DashboardPage[Dashboard Page Component]
    end
    
    subgraph "Data Hooks"
        useAlerts[useAlerts hook]
        useShipments[useShipments hook]
        useFilters[useFilters hook]
    end
    
    subgraph "Child Components"
        Stats[Stats Cards]
        ShipmentsW[Shipments Widget]
        AlertsW[Alerts Widget]
        AnalysisP[Analysis Panel]
    end
    
    DashboardPage --> useAlerts
    DashboardPage --> useShipments
    DashboardPage --> useFilters
    
    useAlerts --> AlertsW
    useAlerts --> AnalysisP
    useAlerts --> Stats
    
    useShipments --> ShipmentsW
    useShipments --> Stats
    
    useFilters --> AlertsW
    
    AlertsW -.Selected Alert.-> AnalysisP
    
    style DashboardPage fill:#61dafb
    style useAlerts fill:#ff4154
    style useShipments fill:#ff4154
    style useFilters fill:#4caf50
```

## Error Handling Flow

```mermaid
graph TD
    Request[API Request]
    Request --> Success{Success?}
    
    Success -->|Yes| Cache[Update Cache]
    Cache --> Render[Render Data]
    
    Success -->|No| ErrorType{Error Type}
    
    ErrorType -->|Network| Retry[Retry Logic]
    ErrorType -->|4xx| UserError[Show User Error]
    ErrorType -->|5xx| ServerError[Show Server Error]
    
    Retry --> RetryCount{Retry Count}
    RetryCount -->|< 3| Request
    RetryCount -->|>= 3| FinalError[Show Final Error]
    
    UserError --> ErrorUI[Error Boundary]
    ServerError --> ErrorUI
    FinalError --> ErrorUI
    
    ErrorUI --> Fallback[Fallback UI]
    
    style Success fill:#4caf50
    style ErrorType fill:#ff9800
    style ErrorUI fill:#f44336
```

## Responsive Layout Strategy

```mermaid
graph LR
    subgraph "Mobile < 600px"
        M1[Stack Layout]
        M2[Stats Cards - Vertical]
        M3[Shipments - Full Width]
        M4[Alerts - Full Width]
        M5[Analysis - Modal]
    end
    
    subgraph "Tablet 600-960px"
        T1[Grid Layout 2 Columns]
        T2[Stats Cards - Horizontal]
        T3[Shipments - Left Column]
        T4[Alerts - Right Column]
        T5[Analysis - Drawer]
    end
    
    subgraph "Desktop > 960px"
        D1[Grid Layout 3 Columns]
        D2[Stats Cards - Horizontal]
        D3[Shipments - Left 40%]
        D4[Alerts - Middle 30%]
        D5[Analysis - Right 30%]
    end
    
    style M1 fill:#2196f3
    style T1 fill:#4caf50
    style D1 fill:#9c27b0
```

## Performance Optimization Strategy

```mermaid
graph TB
    subgraph "Build Time"
        CodeSplit[Code Splitting]
        TreeShake[Tree Shaking]
        Minify[Minification]
    end
    
    subgraph "Runtime"
        Memo[React.memo]
        UseMemo[useMemo]
        UseCallback[useCallback]
        Virtual[Virtual Scrolling]
    end
    
    subgraph "Network"
        Cache[React Query Cache]
        Prefetch[Prefetching]
        Debounce[Debounced Requests]
    end
    
    subgraph "Result"
        FastLoad[Fast Initial Load]
        SmoothUI[Smooth Interactions]
        LowBandwidth[Low Bandwidth Usage]
    end
    
    CodeSplit --> FastLoad
    TreeShake --> FastLoad
    Minify --> FastLoad
    
    Memo --> SmoothUI
    UseMemo --> SmoothUI
    UseCallback --> SmoothUI
    Virtual --> SmoothUI
    
    Cache --> LowBandwidth
    Prefetch --> LowBandwidth
    Debounce --> LowBandwidth
    
    style FastLoad fill:#4caf50
    style SmoothUI fill:#2196f3
    style LowBandwidth fill:#ff9800
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        Dev[Local Dev Server]
        DevAPI[Local Backend]
    end
    
    subgraph "Build Process"
        Vite[Vite Build]
        Bundle[Optimized Bundle]
        Assets[Static Assets]
    end
    
    subgraph "Production"
        CDN[CDN - Static Files]
        Server[Web Server - Nginx/Apache]
        API[Production API]
    end
    
    Dev --> Vite
    DevAPI -.-> Dev
    
    Vite --> Bundle
    Vite --> Assets
    
    Bundle --> CDN
    Assets --> CDN
    
    CDN --> Server
    Server --> API
    
    style Dev fill:#61dafb
    style Vite fill:#646cff
    style CDN fill:#4caf50
    style API fill:#009688
```

## Key Design Decisions

### 1. React Query for Server State
- **Why**: Automatic caching, background refetching, optimistic updates
- **Alternative**: Redux Toolkit Query, SWR
- **Trade-off**: Learning curve vs powerful features

### 2. Material-UI for Components
- **Why**: Comprehensive component library, good TypeScript support, customizable
- **Alternative**: Ant Design, Chakra UI, Custom components
- **Trade-off**: Bundle size vs development speed

### 3. Vite for Build Tool
- **Why**: Fast HMR, modern ESM-based, optimized builds
- **Alternative**: Create React App, Webpack
- **Trade-off**: Newer tool vs proven stability

### 4. TypeScript for Type Safety
- **Why**: Catch errors early, better IDE support, self-documenting
- **Alternative**: JavaScript with JSDoc
- **Trade-off**: Initial setup time vs long-term maintainability

### 5. Polling vs WebSocket
- **Current**: Polling every 30 seconds
- **Future**: WebSocket for real-time updates
- **Reason**: Simpler implementation, sufficient for MVP

## Security Considerations

```mermaid
graph TB
    subgraph "Frontend Security"
        XSS[XSS Prevention]
        CSRF[CSRF Protection]
        Auth[Authentication]
        Env[Environment Variables]
    end
    
    subgraph "Implementation"
        React[React Auto-escaping]
        Tokens[JWT Tokens]
        HTTPS[HTTPS Only]
        Secrets[Secret Management]
    end
    
    XSS --> React
    CSRF --> Tokens
    Auth --> Tokens
    Auth --> HTTPS
    Env --> Secrets
    
    style XSS fill:#f44336
    style CSRF fill:#ff9800
    style Auth fill:#4caf50
```

## Monitoring & Analytics

```mermaid
graph LR
    subgraph "Metrics"
        Performance[Performance Metrics]
        Errors[Error Tracking]
        Usage[Usage Analytics]
    end
    
    subgraph "Tools - Future"
        Sentry[Sentry - Errors]
        Analytics[Google Analytics]
        Vitals[Web Vitals]
    end
    
    Performance --> Vitals
    Errors --> Sentry
    Usage --> Analytics
    
    style Performance fill:#2196f3
    style Errors fill:#f44336
    style Usage fill:#4caf50
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- Project setup with Vite + TypeScript
- API client configuration
- Basic routing structure
- Core type definitions

### Phase 2: Core Features (Week 2)
- Dashboard layout
- Shipments widget
- Alerts widget
- Basic data fetching

### Phase 3: Advanced Features (Week 3)
- AI analysis panel
- Charts and visualizations
- Filtering and sorting
- Auto-refresh

### Phase 4: Polish (Week 4)
- Error handling
- Loading states
- Responsive design
- Performance optimization

### Phase 5: Testing & Documentation
- Unit tests
- Integration tests
- Documentation
- Deployment guide

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Initial Load Time | < 2 seconds | Lighthouse |
| Time to Interactive | < 3 seconds | Lighthouse |
| Bundle Size | < 500KB gzipped | Webpack Bundle Analyzer |
| API Response Time | < 500ms | Network tab |
| Error Rate | < 1% | Error tracking |
| User Satisfaction | > 4/5 | User feedback |
