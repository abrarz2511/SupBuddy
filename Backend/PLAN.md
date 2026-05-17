# SupBuddy - FastAPI Backend Implementation Plan

## System Overview

SupBuddy is a logistics shipment tracking system with SLA monitoring and AI-powered exception analysis. The system tracks shipments through multiple stages:
1. **Shipping Port** → 2. **Customs** → 3. **Delivery Center** → 4. **Regional Hub** → 5. **End Customer**

At each location, the shipment is received and status is updated with timestamp. The SLA Rules Engine monitors these updates and triggers the Freight Exception Analyst Agent when anomalies are detected.

## Technology Stack

- **Backend Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM (async support)
- **Validation**: Pydantic v2
- **Task Scheduling**: APScheduler
- **HTTP Client**: httpx (async)
- **Containerization**: Docker & Docker Compose

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   REST API   │    │  APScheduler │    │ Agent Gateway│      │
│  │   Endpoints  │    │   (Cron)     │    │  (Watsonx)   │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                    │              │
│  ┌──────▼───────────────────▼────────────────────▼───────┐     │
│  │              Core Services Layer                       │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │     │
│  │  │Tracking  │ │Schedule  │ │SLA Rules │ │Context   │ │     │
│  │  │Service   │ │Service   │ │Engine    │ │Tools     │ │     │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │     │
│  └────────────────────────┬───────────────────────────────┘     │
│                           │                                     │
│  ┌────────────────────────▼───────────────────────────────┐     │
│  │           Repository/Database Layer                     │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │     │
│  │  │Shipment  │ │Schedule  │ │SLA Rule  │ │Alert     │ │     │
│  │  │Repo      │ │Repo      │ │Repo      │ │Repo      │ │     │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │     │
│  └────────────────────────┬───────────────────────────────┘     │
│                           │                                     │
│                    ┌──────▼──────┐                              │
│                    │  PostgreSQL │                              │
│                    └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Schema Design

### 1. Shipments Table
Stores core shipment information and current status.

```sql
CREATE TABLE shipments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_number VARCHAR(100) UNIQUE NOT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    current_status VARCHAR(50) NOT NULL,
    current_location VARCHAR(255),
    customer_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_tracking_number (tracking_number),
    INDEX idx_current_status (current_status),
    INDEX idx_customer_id (customer_id)
);
```

**Fields:**
- `id`: Unique identifier (UUID)
- `tracking_number`: External tracking reference
- `origin`: Starting location
- `destination`: Final delivery address
- `current_status`: Current milestone status (PORT_RECEIVED, CUSTOMS_CLEARED, etc.)
- `current_location`: Current physical location
- `customer_id`: Reference to customer
- `created_at`, `updated_at`: Audit timestamps

---

### 2. Milestones Table
Tracks each checkpoint in the shipment journey with timestamps.

```sql
CREATE TABLE milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id UUID NOT NULL REFERENCES shipments(id) ON DELETE CASCADE,
    milestone_type VARCHAR(50) NOT NULL,
    location VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    received BOOLEAN DEFAULT FALSE,
    approved BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_shipment_id (shipment_id),
    INDEX idx_milestone_type (milestone_type),
    INDEX idx_timestamp (timestamp)
);
```

**Milestone Types:**
- `PORT_RECEIVED`: Shipment received at port
- `CUSTOMS_SUBMITTED`: Submitted to customs
- `CUSTOMS_CLEARED`: Cleared by customs
- `DELIVERY_CENTER_RECEIVED`: Received at delivery center
- `REGIONAL_HUB_RECEIVED`: Received at regional hub
- `OUT_FOR_DELIVERY`: Out for final delivery
- `DELIVERED`: Delivered to customer

**Fields:**
- `received`: Boolean flag indicating package received at location
- `approved`: Boolean flag for approval status (e.g., customs clearance)
- `timestamp`: When the milestone event occurred

---

### 3. Schedules Table
Stores predetermined expected timelines for shipments.

```sql
CREATE TABLE schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id UUID NOT NULL REFERENCES shipments(id) ON DELETE CASCADE,
    milestone_type VARCHAR(50) NOT NULL,
    expected_location VARCHAR(255) NOT NULL,
    expected_arrival TIMESTAMP WITH TIME ZONE NOT NULL,
    expected_departure TIMESTAMP WITH TIME ZONE,
    buffer_minutes INTEGER DEFAULT 60,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_shipment_id (shipment_id),
    INDEX idx_expected_arrival (expected_arrival),
    UNIQUE (shipment_id, milestone_type)
);
```

**Fields:**
- `expected_arrival`: When shipment should arrive at this milestone
- `expected_departure`: When shipment should leave this milestone
- `buffer_minutes`: Acceptable delay buffer before triggering alert

---

### 4. SLA Rules Table
Defines configurable SLA rules for detecting issues.

```sql
CREATE TABLE sla_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(100) UNIQUE NOT NULL,
    rule_type VARCHAR(50) NOT NULL,
    milestone_type VARCHAR(50),
    condition_json JSONB NOT NULL,
    threshold_minutes INTEGER,
    priority VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_rule_type (rule_type),
    INDEX idx_is_active (is_active)
);
```

**Rule Types:**
- `MISSING_UPDATE`: Milestone not received when expected
- `LATE_ARRIVAL`: Milestone received but later than expected
- `STALE_STATUS`: No updates for extended period
- `CUSTOMS_DELAY`: Customs clearance taking too long
- `LOCATION_MISMATCH`: Shipment at unexpected location

**Condition JSON Example:**
```json
{
  "check_type": "time_difference",
  "compare_field": "expected_arrival",
  "operator": "greater_than",
  "threshold_minutes": 120,
  "severity_escalation": {
    "60": "LOW",
    "120": "MEDIUM",
    "240": "HIGH",
    "480": "CRITICAL"
  }
}
```

---

### 5. Alerts Table
Stores detected SLA violations and exceptions.

```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id UUID NOT NULL REFERENCES shipments(id) ON DELETE CASCADE,
    sla_rule_id UUID REFERENCES sla_rules(id),
    alert_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(50) DEFAULT 'OPEN',
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    backend_reason TEXT,
    milestone_type VARCHAR(50),
    expected_time TIMESTAMP WITH TIME ZONE,
    actual_time TIMESTAMP WITH TIME ZONE,
    delay_minutes INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_shipment_id (shipment_id),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_detected_at (detected_at)
);
```

**Alert Status:**
- `OPEN`: Newly detected, awaiting analysis
- `ANALYZING`: Sent to agent for analysis
- `ANALYZED`: Agent analysis complete
- `RESOLVED`: Issue resolved
- `CLOSED`: Alert closed without resolution

**Priority Levels:**
- `LOW`: Minor delay within acceptable range
- `MEDIUM`: Moderate delay requiring attention
- `HIGH`: Significant delay impacting delivery
- `CRITICAL`: Severe issue requiring immediate action

---

### 6. Alert Analysis Table
Stores AI agent analysis results for alerts.

```sql
CREATE TABLE alert_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    likely_cause TEXT NOT NULL,
    risk_priority VARCHAR(20) NOT NULL,
    confidence_level DECIMAL(3,2) NOT NULL,
    supporting_evidence JSONB,
    recommended_action TEXT NOT NULL,
    external_factors JSONB,
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    agent_version VARCHAR(50),
    
    INDEX idx_alert_id (alert_id),
    INDEX idx_analyzed_at (analyzed_at),
    UNIQUE (alert_id)
);
```

**Supporting Evidence JSON Example:**
```json
{
  "weather_impact": {
    "condition": "heavy_rain",
    "severity": "moderate",
    "location": "Port of Los Angeles"
  },
  "traffic_impact": {
    "delay_minutes": 45,
    "cause": "highway_closure"
  },
  "historical_pattern": {
    "similar_delays": 3,
    "average_delay": 120,
    "typical_resolution": "24_hours"
  }
}
```

---

## Project Structure

```
supbuddy/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── shipment.py
│   │   ├── milestone.py
│   │   ├── schedule.py
│   │   ├── sla_rule.py
│   │   ├── alert.py
│   │   └── alert_analysis.py
│   │
│   ├── schemas/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── shipment.py
│   │   ├── milestone.py
│   │   ├── schedule.py
│   │   ├── sla_rule.py
│   │   ├── alert.py
│   │   └── agent.py
│   │
│   ├── api/                       # API routes
│   │   ├── __init__.py
│   │   ├── deps.py               # Dependencies (DB session, etc.)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── shipments.py
│   │   │   ├── schedules.py
│   │   │   ├── sla_rules.py
│   │   │   ├── alerts.py
│   │   │   └── agent.py
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── tracking_service.py
│   │   ├── schedule_service.py
│   │   ├── sla_engine.py
│   │   ├── agent_gateway.py
│   │   └── notification_service.py
│   │
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── shipment_repo.py
│   │   ├── milestone_repo.py
│   │   ├── schedule_repo.py
│   │   ├── sla_rule_repo.py
│   │   └── alert_repo.py
│   │
│   ├── core/                      # Core utilities
│   │   ├── __init__.py
│   │   ├── database.py           # Database connection
│   │   ├── logging.py            # Logging configuration
│   │   └── scheduler.py          # APScheduler setup
│   │
│   └── context_tools/             # External API integrations (mock)
│       ├── __init__.py
│       ├── weather.py
│       ├── traffic.py
│       ├── port_status.py
│       ├── news.py
│       └── shipment_history.py
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── test_repositories/
│
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── alembic.ini
```

---

## Core Services Design

### 1. Tracking Service
**Purpose**: Handle shipment milestone updates and status tracking.

**Key Methods:**
- `create_shipment(tracking_number, origin, destination, customer_id)` → Shipment
- `update_milestone(shipment_id, milestone_type, location, received, approved, timestamp)` → Milestone
- `get_shipment_status(tracking_number)` → ShipmentStatus
- `get_shipment_timeline(shipment_id)` → List[Milestone]
- `update_shipment_location(shipment_id, location, status)` → Shipment

**Responsibilities:**
- Create and manage shipment records
- Record milestone events with timestamps
- Update current shipment status and location
- Provide shipment tracking information

---

### 2. Schedule Service
**Purpose**: Manage predetermined schedules and expected arrival times.

**Key Methods:**
- `create_schedule(shipment_id, milestones)` → List[Schedule]
- `get_schedule(shipment_id)` → List[Schedule]
- `update_expected_time(schedule_id, new_time)` → Schedule
- `get_next_milestone(shipment_id)` → Schedule
- `calculate_eta(shipment_id, current_location)` → datetime

**Responsibilities:**
- Store expected timeline for each shipment
- Provide expected arrival/departure times
- Calculate estimated time of arrival
- Support schedule adjustments

---

### 3. SLA Rules Engine
**Purpose**: Detect missing, late, or risky updates by comparing actual vs expected times.

**Key Methods:**
- `evaluate_shipment(shipment_id)` → List[Alert]
- `check_missing_updates(shipment_id)` → Optional[Alert]
- `check_late_arrivals(shipment_id)` → Optional[Alert]
- `check_stale_status(shipment_id)` → Optional[Alert]
- `calculate_delay(expected_time, actual_time)` → int (minutes)
- `determine_priority(delay_minutes, rule)` → Priority
- `deduplicate_alerts(shipment_id, alert_type)` → bool

**SLA Rule Evaluation Logic:**
```python
def evaluate_shipment(shipment_id):
    alerts = []
    
    # Get shipment and schedule
    shipment = get_shipment(shipment_id)
    schedule = get_schedule(shipment_id)
    milestones = get_milestones(shipment_id)
    
    # Check each scheduled milestone
    for scheduled_milestone in schedule:
        actual_milestone = find_milestone(milestones, scheduled_milestone.type)
        
        # Check for missing update
        if not actual_milestone and is_overdue(scheduled_milestone):
            alert = create_alert(
                type="MISSING_UPDATE",
                priority=calculate_priority(scheduled_milestone),
                reason=f"No {scheduled_milestone.type} update received"
            )
            alerts.append(alert)
        
        # Check for late arrival
        elif actual_milestone and is_late(actual_milestone, scheduled_milestone):
            delay = calculate_delay(scheduled_milestone.expected_arrival, 
                                   actual_milestone.timestamp)
            alert = create_alert(
                type="LATE_ARRIVAL",
                priority=determine_priority(delay, scheduled_milestone),
                delay_minutes=delay
            )
            alerts.append(alert)
    
    # Check for stale status
    if is_stale(shipment):
        alert = create_alert(
            type="STALE_STATUS",
            priority="MEDIUM",
            reason="No updates for extended period"
        )
        alerts.append(alert)
    
    return deduplicate_and_save(alerts)
```

**Responsibilities:**
- Periodically evaluate all active shipments
- Compare actual milestones against schedule
- Detect missing, late, or stale updates
- Calculate delay and determine priority
- Create alerts for meaningful issues
- Deduplicate against existing open alerts
- Trigger agent gateway for high-priority alerts

---

### 4. Agent Gateway Service
**Purpose**: Interface with Watsonx Freight Exception Analyst Agent.

**Key Methods:**
- `analyze_alert(alert_id)` → AlertAnalysis
- `get_shipment_context(shipment_id)` → ShipmentContext
- `call_watsonx_agent(context)` → AgentResponse
- `save_analysis(alert_id, analysis)` → AlertAnalysis
- `trigger_notification(alert_id)` → bool

**Agent Context Structure:**
```python
{
    "alert": {
        "id": "uuid",
        "type": "LATE_ARRIVAL",
        "priority": "HIGH",
        "detected_at": "2026-05-16T10:00:00Z"
    },
    "shipment": {
        "tracking_number": "SHIP123456",
        "origin": "Port of LA",
        "destination": "New York, NY",
        "current_location": "Los Angeles, CA",
        "current_status": "CUSTOMS_SUBMITTED"
    },
    "timeline": [
        {
            "milestone": "PORT_RECEIVED",
            "expected": "2026-05-15T08:00:00Z",
            "actual": "2026-05-15T08:15:00Z",
            "delay_minutes": 15
        },
        {
            "milestone": "CUSTOMS_CLEARED",
            "expected": "2026-05-15T14:00:00Z",
            "actual": null,
            "delay_minutes": 1200
        }
    ],
    "sla_breach": {
        "rule_name": "Customs Clearance Delay",
        "threshold_minutes": 360,
        "actual_delay": 1200
    },
    "next_milestones": [
        {
            "type": "DELIVERY_CENTER_RECEIVED",
            "expected": "2026-05-16T10:00:00Z",
            "at_risk": true
        }
    ],
    "business_impact": {
        "customer_priority": "HIGH",
        "delivery_commitment": "2026-05-18T17:00:00Z",
        "risk_level": "HIGH"
    },
    "external_signals": {
        "weather": "...",
        "traffic": "...",
        "port_status": "...",
        "customs_status": "..."
    }
}
```

**Agent Response Structure:**
```python
{
    "likely_cause": "Customs backlog due to increased inspection requirements",
    "risk_priority": "HIGH",
    "confidence_level": 0.85,
    "supporting_evidence": {
        "customs_status": "High volume processing delays reported",
        "historical_pattern": "Similar delays in past 3 shipments from this port",
        "external_factors": "New inspection protocols implemented this week"
    },
    "recommended_action": "Contact customs broker for expedited processing. Consider alternative routing for future shipments.",
    "estimated_resolution": "4-6 hours"
}
```

**Responsibilities:**
- Gather comprehensive context for alerts
- Call Watsonx agent with structured data
- Receive and parse agent analysis
- Store analysis results
- Trigger notifications to users

---

### 5. Context Tools (Mock Implementations)

#### Weather Lookup
```python
async def get_weather_impact(location: str, timestamp: datetime) -> dict:
    """Mock weather data for location"""
    return {
        "condition": "clear",
        "temperature": 72,
        "impact_level": "none",
        "alerts": []
    }
```

#### Traffic Lookup
```python
async def get_traffic_conditions(location: str) -> dict:
    """Mock traffic data"""
    return {
        "congestion_level": "moderate",
        "estimated_delay_minutes": 15,
        "incidents": []
    }
```

#### Port Status Lookup
```python
async def get_port_status(port_name: str) -> dict:
    """Mock port operational status"""
    return {
        "operational_status": "normal",
        "congestion_level": "low",
        "average_processing_time_hours": 4,
        "delays_reported": false
    }
```

#### News/Disruption Lookup
```python
async def get_local_disruptions(location: str) -> dict:
    """Mock local news and disruptions"""
    return {
        "disruptions": [],
        "news_items": [],
        "impact_level": "none"
    }
```

#### Shipment History Lookup
```python
async def get_shipment_history(customer_id: str, route: str) -> dict:
    """Mock historical shipment data"""
    return {
        "total_shipments": 50,
        "average_delay_minutes": 30,
        "common_issues": ["customs_delay"],
        "success_rate": 0.94
    }
```

---

## API Endpoints Design

### Shipment Tracking APIs

#### POST /api/v1/shipments
Create a new shipment.
```json
Request:
{
  "tracking_number": "SHIP123456",
  "origin": "Port of Los Angeles",
  "destination": "New York, NY",
  "customer_id": "CUST001"
}

Response:
{
  "id": "uuid",
  "tracking_number": "SHIP123456",
  "current_status": "CREATED",
  "created_at": "2026-05-16T10:00:00Z"
}
```

#### POST /api/v1/shipments/{shipment_id}/milestones
Update shipment milestone.
```json
Request:
{
  "milestone_type": "PORT_RECEIVED",
  "location": "Port of Los Angeles",
  "received": true,
  "approved": true,
  "timestamp": "2026-05-16T08:00:00Z",
  "notes": "Package received in good condition"
}

Response:
{
  "id": "uuid",
  "shipment_id": "uuid",
  "milestone_type": "PORT_RECEIVED",
  "status": "COMPLETED",
  "timestamp": "2026-05-16T08:00:00Z"
}
```

#### GET /api/v1/shipments/{tracking_number}
Get shipment status and timeline.
```json
Response:
{
  "shipment": {
    "id": "uuid",
    "tracking_number": "SHIP123456",
    "current_status": "CUSTOMS_CLEARED",
    "current_location": "Los Angeles Customs"
  },
  "timeline": [
    {
      "milestone_type": "PORT_RECEIVED",
      "timestamp": "2026-05-16T08:00:00Z",
      "location": "Port of LA"
    }
  ],
  "next_milestone": {
    "type": "DELIVERY_CENTER_RECEIVED",
    "expected_at": "2026-05-16T14:00:00Z"
  }
}
```

---

### Schedule Management APIs

#### POST /api/v1/schedules
Create schedule for shipment.
```json
Request:
{
  "shipment_id": "uuid",
  "milestones": [
    {
      "milestone_type": "PORT_RECEIVED",
      "expected_location": "Port of LA",
      "expected_arrival": "2026-05-16T08:00:00Z",
      "buffer_minutes": 60
    },
    {
      "milestone_type": "CUSTOMS_CLEARED",
      "expected_location": "LA Customs",
      "expected_arrival": "2026-05-16T14:00:00Z",
      "buffer_minutes": 120
    }
  ]
}
```

#### GET /api/v1/schedules/{shipment_id}
Get schedule for shipment.

---

### SLA Rules APIs

#### POST /api/v1/sla-rules
Create SLA rule.
```json
Request:
{
  "rule_name": "Customs Delay Alert",
  "rule_type": "LATE_ARRIVAL",
  "milestone_type": "CUSTOMS_CLEARED",
  "threshold_minutes": 360,
  "priority": "HIGH",
  "condition_json": {
    "check_type": "time_difference",
    "operator": "greater_than"
  }
}
```

#### GET /api/v1/sla-rules
List all SLA rules.

#### PUT /api/v1/sla-rules/{rule_id}
Update SLA rule.

---

### Alert Management APIs

#### GET /api/v1/alerts
List alerts with filters.
```
Query params: status, priority, shipment_id, from_date, to_date
```

#### GET /api/v1/alerts/{alert_id}
Get alert details with analysis.
```json
Response:
{
  "alert": {
    "id": "uuid",
    "shipment_id": "uuid",
    "alert_type": "LATE_ARRIVAL",
    "priority": "HIGH",
    "status": "ANALYZED",
    "detected_at": "2026-05-16T10:00:00Z"
  },
  "analysis": {
    "likely_cause": "Customs backlog",
    "confidence_level": 0.85,
    "recommended_action": "Contact customs broker"
  }
}
```

#### PUT /api/v1/alerts/{alert_id}/resolve
Resolve an alert.

---

### Agent Integration APIs

#### POST /api/v1/agent/analyze
Trigger agent analysis (called by SLA engine).
```json
Request:
{
  "alert_id": "uuid"
}

Response:
{
  "analysis_id": "uuid",
  "status": "ANALYZING"
}
```

#### GET /api/v1/agent/context/{shipment_id}
Get shipment context for agent (called by agent).
```json
Response:
{
  "shipment": {...},
  "timeline": [...],
  "sla_breach": {...},
  "external_signals": {...}
}
```

#### POST /api/v1/agent/analysis
Save agent analysis result (called by agent).
```json
Request:
{
  "alert_id": "uuid",
  "likely_cause": "...",
  "risk_priority": "HIGH",
  "confidence_level": 0.85,
  "supporting_evidence": {...},
  "recommended_action": "..."
}
```

#### POST /api/v1/notifications
Send notification to user.

---

## Scheduled Tasks (APScheduler)

### 1. Tracking Data Pull Job
**Schedule**: Every 5 minutes
**Purpose**: Pull latest tracking updates from external systems

```python
@scheduler.scheduled_job('interval', minutes=5)
async def pull_tracking_data():
    # Pull updates from tracking system
    # Normalize milestone events
    # Update database
    pass
```

### 2. SLA Evaluation Job
**Schedule**: Every 10 minutes
**Purpose**: Evaluate all active shipments against SLA rules

```python
@scheduler.scheduled_job('interval', minutes=10)
async def evaluate_sla_rules():
    active_shipments = await get_active_shipments()
    for shipment in active_shipments:
        alerts = await sla_engine.evaluate_shipment(shipment.id)
        for alert in alerts:
            if alert.priority in ['HIGH', 'CRITICAL']:
                await agent_gateway.analyze_alert(alert.id)
```

### 3. Alert Cleanup Job
**Schedule**: Daily at 2 AM
**Purpose**: Archive old resolved alerts

```python
@scheduler.scheduled_job('cron', hour=2)
async def cleanup_old_alerts():
    # Archive alerts older than 90 days
    pass
```

---

## Configuration Management

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/supbuddy
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# API
API_V1_PREFIX=/api/v1
API_TITLE=SupBuddy Logistics API
API_VERSION=1.0.0
CORS_ORIGINS=["http://localhost:3000"]

# Scheduler
SCHEDULER_ENABLED=true
TRACKING_PULL_INTERVAL_MINUTES=5
SLA_EVAL_INTERVAL_MINUTES=10

# Agent
WATSONX_API_URL=https://api.watsonx.ai/v1
WATSONX_API_KEY=your_api_key_here
AGENT_TIMEOUT_SECONDS=30

# External APIs (Mock for now)
WEATHER_API_KEY=mock
TRAFFIC_API_KEY=mock
PORT_API_KEY=mock

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Settings Class (Pydantic)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_v1_prefix: str = "/api/v1"
    watsonx_api_url: str
    watsonx_api_key: str
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
```

---

## Dependencies (requirements.txt)

```txt
# FastAPI
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
alembic==1.13.1

# Validation
pydantic==2.5.3
pydantic-settings==2.1.0
email-validator==2.1.0

# Scheduling
apscheduler==3.10.4

# HTTP Client
httpx==0.26.0

# Utilities
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0

# Development
black==23.12.1
flake8==7.0.0
mypy==1.8.0
```

---

## Docker Setup

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://supbuddy:password@db:5432/supbuddy
    depends_on:
      - db
    volumes:
      - ./app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=supbuddy
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=supbuddy
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Implementation Phases

### Phase 1: Foundation (Focus for Initial Implementation)
1. ✅ Project structure setup
2. ✅ Database models (SQLAlchemy)
3. ✅ Pydantic schemas
4. ✅ Database connection and session management
5. ✅ Basic CRUD repositories

### Phase 2: Core Services
6. ✅ Tracking Service implementation
7. ✅ Schedule Service implementation
8. ✅ SLA Rules Engine implementation
9. ✅ Database Service layer

### Phase 3: API Layer
10. ✅ Shipment tracking endpoints
11. ✅ Schedule management endpoints
12. ✅ SLA rules endpoints
13. ✅ Alert management endpoints

### Phase 4: Scheduling & Monitoring
14. ✅ APScheduler setup
15. ✅ Periodic tracking data pull
16. ✅ Periodic SLA evaluation

### Phase 5: Agent Integration (Future)
17. ⏳ Agent Gateway service (mock)
18. ⏳ Context tools (mock implementations)
19. ⏳ Agent API endpoints
20. ⏳ Notification service

### Phase 6: Production Ready
21. ⏳ Docker setup
22. ⏳ Logging configuration
23. ⏳ Error handling middleware
24. ⏳ API documentation
25. ⏳ Testing suite

---

## Next Steps

Based on your preference to **focus on SLA Rules Engine and tracking service first**, here's the recommended implementation order:

1. **Set up project structure** - Create directory layout and basic files
2. **Database models** - Implement SQLAlchemy models for core entities
3. **Pydantic schemas** - Create request/response validation schemas
4. **Database connection** - Set up async PostgreSQL connection
5. **Tracking Service** - Implement shipment and milestone tracking
6. **Schedule Service** - Implement schedule management
7. **SLA Rules Engine** - Implement the core detection logic
8. **API endpoints** - Create REST APIs for the above services
9. **APScheduler** - Set up periodic SLA evaluation
10. **Agent Gateway (mock)** - Add placeholder for future integration

This plan provides a solid foundation for the SupBuddy logistics tracking system. Once you approve this plan, we can switch to Code mode to begin implementation!