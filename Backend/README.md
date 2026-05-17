# SupBuddy - Logistics Tracking System API

A FastAPI-based backend system for tracking shipments through the logistics network with AI-powered exception analysis.

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- IBM Watsonx API access (for AI agent)

### Installation

1. **Clone and setup environment:**

```bash
cd SupBuddy
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment variables:**

```bash
cp .env.example .env
# Edit .env with your database and API credentials
```

3. **Initialize database:**

Postgresql is required to run the database. You can install it from the official website. Once installed, you can create a new database and a new user with the following commands:

Find the path to your PostgreSQL installation

```bash

ls "/c/Program Files/PostgreSQL"

```

Run psql:

```bash
"/c/Program Files/PostgreSQL/17/bin/psql.exe" -U postgres
```

```bash
CREATE DATABASE supbuddy;
CREATE USER YOUR_USERNAME WITH PASSWORD 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE supbuddy TO YOUR_USERNAME;
ALTER DATABASE supbuddy OWNER TO YOUR_USERNAME;
```

if user already exists:

```bash
ALTER USER YOUR_USERNAME WITH PASSWORD 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE supbuddy TO YOUR_USERNAME;
ALTER DATABASE supbuddy OWNER TO YOUR_USERNAME;
```

exit:

```bash
\q
```

Edit the `DATABASE_URL` in `.env` with your PostgreSQL information.

```
DATABASE_URL=postgresql+asyncpg://myuser:mypassword@localhost:5432/supbuddy
```

4. **Run the application:**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the API:**

- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## API Endpoints

### Shipment Tracking

#### Create Shipment

```http
POST /api/v1/shipments
Content-Type: application/json

{
  "tracking_number": "SHIP-2024-001234",
  "origin": "Shanghai Port, China",
  "destination": "Los Angeles Port, USA",
  "customer_id": "CUST-5678"
}
```

#### Get Shipment Status

```http
GET /api/v1/shipments/{tracking_number}
```

Response:

```json
{
  "id": "uuid",
  "tracking_number": "SHIP-2024-001234",
  "current_status": "CUSTOMS_CLEARED",
  "current_location": "Los Angeles Customs",
  "origin": "Shanghai Port, China",
  "destination": "Los Angeles Port, USA",
  "milestones": [...],
  "schedules": [...],
  "created_at": "2024-01-15T08:00:00Z"
}
```

#### Update Milestone

```http
POST /api/v1/shipments/{shipment_id}/milestones
Content-Type: application/json

{
  "milestone_type": "PORT_RECEIVED",
  "location": "Los Angeles Port",
  "received": true,
  "approved": true,
  "timestamp": "2024-01-15T08:00:00Z",
  "notes": "Package received in good condition"
}
```

**Milestone Types:**

- `PORT_RECEIVED` - Shipment received at port
- `CUSTOMS_SUBMITTED` - Submitted to customs
- `CUSTOMS_CLEARED` - Cleared by customs
- `DELIVERY_CENTER_RECEIVED` - Received at delivery center
- `REGIONAL_HUB_RECEIVED` - Received at regional hub
- `OUT_FOR_DELIVERY` - Out for final delivery
- `DELIVERED` - Delivered to customer

---

### Schedule Management

#### Create Schedule

```http
POST /api/v1/schedules
Content-Type: application/json

{
  "shipment_id": "uuid",
  "milestones": [
    {
      "milestone_type": "PORT_RECEIVED",
      "expected_location": "Los Angeles Port",
      "expected_arrival": "2024-01-15T08:00:00Z",
      "buffer_minutes": 60
    },
    {
      "milestone_type": "CUSTOMS_CLEARED",
      "expected_location": "LA Customs",
      "expected_arrival": "2024-01-15T14:00:00Z",
      "buffer_minutes": 120
    }
  ]
}
```

#### Get Schedule

```http
GET /api/v1/schedules/{shipment_id}
```

---

### Alert Management

#### List Alerts

```http
GET /api/v1/alerts?status=OPEN&priority=HIGH&limit=50
```

Query Parameters:

- `shipment_id` - Filter by shipment
- `status` - Filter by status (OPEN, ANALYZING, ANALYZED, RESOLVED, CLOSED)
- `priority` - Filter by priority (LOW, MEDIUM, HIGH, CRITICAL)
- `from_date` - Filter alerts after this date
- `to_date` - Filter alerts before this date
- `skip` - Pagination offset (default: 0)
- `limit` - Results per page (default: 50)

#### Get Alert Details

```http
GET /api/v1/alerts/{alert_id}
```

Response includes AI agent analysis:

```json
{
  "alert": {
    "id": "uuid",
    "shipment_id": "uuid",
    "alert_type": "LATE_ARRIVAL",
    "priority": "HIGH",
    "status": "ANALYZED",
    "detected_at": "2024-01-15T10:00:00Z",
    "delay_minutes": 180
  },
  "analysis": {
    "likely_cause": "Customs backlog due to increased inspection requirements",
    "risk_priority": "HIGH",
    "confidence_level": 0.85,
    "supporting_evidence": {
      "customs_status": "High volume processing delays reported",
      "weather": {...},
      "traffic": {...}
    }
  }
}
```

#### Trigger Alert Analysis

```http
POST /api/v1/alerts/{alert_id}/analyze
```

Manually trigger AI agent analysis for an alert.

#### Resolve Alert

```http
PUT /api/v1/alerts/{alert_id}/resolve
Content-Type: application/json

{
  "resolution_notes": "Issue resolved - shipment cleared customs"
}
```

---

### Agent Integration

#### Get Shipment Context (for AI Agent)

```http
GET /api/v1/agent/context/{shipment_id}
```

Returns comprehensive context for AI analysis including:

- Shipment details and timeline
- SLA breach information
- External signals (weather, traffic, port status, news)
- Historical patterns

#### Save Agent Analysis

```http
POST /api/v1/agent/analysis
Content-Type: application/json

{
  "alert_id": "uuid",
  "likely_cause": "Customs backlog",
  "risk_priority": "HIGH",
  "confidence_level": 0.85,
  "supporting_evidence": {...},
  "external_factors": {...}
}
```

---

## System Features

### 1. Shipment Tracking

- Track shipments through multiple stages (Port → Customs → Delivery Center → Regional Hub → Customer)
- Record milestone events with timestamps
- Update shipment status and location in real-time
- Support for multiple carriers and routes

### 2. Schedule Management

- Define expected timelines for each shipment
- Set buffer times for acceptable delays
- Track expected vs actual arrival times
- Support for complex multi-leg journeys

### 3. SLA Rules Engine

Automatically detects issues by comparing actual vs expected times:

**Rule Types:**

- **MISSING_UPDATE** - Milestone not received when expected
- **LATE_ARRIVAL** - Milestone received but later than expected
- **STALE_STATUS** - No updates for extended period
- **CUSTOMS_DELAY** - Customs clearance taking too long
- **LOCATION_MISMATCH** - Shipment at unexpected location

**Priority Levels:**

- **LOW** - Minor delay within acceptable range
- **MEDIUM** - Moderate delay requiring attention
- **HIGH** - Significant delay impacting delivery
- **CRITICAL** - Severe issue requiring immediate action

### 4. AI-Powered Exception Analysis

IBM Watsonx Freight Exception Analyst Agent provides:

- Root cause analysis
- Risk assessment
- Confidence scoring
- Supporting evidence from multiple sources
- Recommended actions

### 5. Context Collection

Gathers external data to support analysis:

- **Weather Data** - NOAA Weather.gov API
- **Traffic Data** - TomTom Routing API
- **Port Status** - News-based port operations monitoring
- **Local Disruptions** - GDELT news aggregation
- **Historical Patterns** - Past shipment performance

### 6. Automated Monitoring

APScheduler runs periodic background jobs:

- **SLA Evaluation** - Every 10 minutes (configurable)
- **Tracking Data Pull** - Every 5 minutes (configurable)
- **Alert Cleanup** - Daily at 2 AM
- **Agent Analysis** - Automatic for HIGH/CRITICAL alerts

---

## Core Services

### TrackingService

Manages shipments and milestone updates:

- Create and retrieve shipments
- Record milestone events
- Update shipment status
- Query shipment timeline

### ScheduleService

Handles expected timelines:

- Create schedules for shipments
- Bulk schedule creation
- Retrieve and update schedules
- Calculate ETAs

### SLAEngine

Evaluates shipments against rules:

- Load rules from YAML configuration
- Detect missing, late, or stale updates
- Calculate delays and priorities
- Create alerts for violations
- Deduplicate alerts

### AlertService

Orchestrates alert workflow:

- List and filter alerts
- Trigger AI agent analysis
- Store analysis results
- Resolve and close alerts
- Track alert lifecycle

### AgentGateway

Interfaces with IBM Watsonx:

- Format requests for Watsonx API
- Handle authentication
- Parse agent responses
- Error handling and retries

### ContextService

Collects external context:

- Weather conditions
- Traffic status
- Port operations
- News and disruptions
- Historical shipment data

---

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/supbuddy
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# API
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000"]

# Scheduler
SCHEDULER_ENABLED=true
SLA_EVAL_INTERVAL_MINUTES=10
TRACKING_PULL_INTERVAL_MINUTES=5

# IBM Watsonx Agent
WATSONX_API_URL=https://api.watsonx.ai/v1
WATSONX_API_KEY=your_api_key_here
AGENT_TIMEOUT_SECONDS=30

# External APIs
WEATHER_API_KEY=your_key
TRAFFIC_API_KEY=your_key
PORT_API_KEY=your_key
NEWS_API_KEY=your_key

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # or 'text' for development
```

### SLA Rules Configuration

Edit `app/config/sla_rules.yaml` to customize SLA rules:

```yaml
rules:
  - name: "Customs Clearance Delay"
    type: "LATE_ARRIVAL"
    milestone_type: "CUSTOMS_CLEARED"
    threshold_minutes: 360
    priority: "HIGH"
    description: "Alert when customs clearance exceeds 6 hours"

  - name: "Missing Port Receipt"
    type: "MISSING_UPDATE"
    milestone_type: "PORT_RECEIVED"
    threshold_minutes: 120
    priority: "CRITICAL"
    description: "Alert when port receipt is missing after 2 hours"
```

---

## Database Schema

### Core Tables

**shipments** - Main shipment records

- `id`, `tracking_number`, `origin`, `destination`
- `current_status`, `current_location`, `customer_id`
- `created_at`, `updated_at`

**milestones** - Checkpoint events

- `id`, `shipment_id`, `milestone_type`, `location`
- `status`, `received`, `approved`, `timestamp`
- `notes`, `created_at`

**schedules** - Expected timelines

- `id`, `shipment_id`, `milestone_type`
- `expected_location`, `expected_arrival`, `expected_departure`
- `buffer_minutes`, `created_at`

**alerts** - SLA violations

- `id`, `shipment_id`, `sla_rule_id`, `alert_type`
- `priority`, `status`, `detected_at`, `resolved_at`
- `backend_reason`, `milestone_type`, `delay_minutes`

**alert_analyses** - AI agent results

- `id`, `alert_id`, `likely_cause`, `risk_priority`
- `confidence_level`, `supporting_evidence`
- `external_factors`, `analyzed_at`, `agent_version`

---

## Development

### Project Structure

```
SupBuddy/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Database, logging, scheduler
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── context_tools/   # External API integrations
│   └── config/          # Configuration files
├── tests/               # Test suite
├── alembic/             # Database migrations
├── main.py              # Application entry point
└── requirements.txt     # Dependencies
```

### Running Tests

```bash
pytest tests/ -v --cov=app
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Logging

**Development (colored console):**

```bash
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

**Production (JSON for log aggregation):**

```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Monitoring

### Scheduler Status

```http
GET /api/v1/scheduler/status
```

Returns status of all background jobs:

```json
{
  "status": "running",
  "jobs": [
    {
      "id": "sla_evaluation",
      "name": "SLA Rules Evaluation",
      "next_run": "2024-01-15T10:10:00Z",
      "trigger": "interval[0:10:00]"
    }
  ]
}
```

### Health Check

```http
GET /health
```

---

## Integration Guide

### Integrating with Frontend

1. **Authentication**: Add JWT token to headers

```javascript
headers: {
  'Authorization': 'Bearer YOUR_TOKEN',
  'Content-Type': 'application/json'
}
```

2. **WebSocket for Real-time Updates** (future):

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/alerts");
ws.onmessage = (event) => {
  const alert = JSON.parse(event.data);
  // Handle new alert
};
```

### Integrating with External Systems

1. **Carrier APIs**: Implement in `TrackingService.pull_tracking_data()`
2. **Notification Services**: Implement in `AlertService.send_notification()`
3. **Custom Context Tools**: Add to `app/context_tools/`

---

## Troubleshooting

### Common Issues

**Database Connection Error:**

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify DATABASE_URL in .env
```

**Scheduler Not Running:**

```bash
# Check SCHEDULER_ENABLED=true in .env
# View logs for scheduler startup messages
```

**Agent Analysis Failing:**

```bash
# Verify WATSONX_API_KEY is correct
# Check agent timeout settings
# Review logs for API errors
```

---
