"""
Pydantic schemas for API request/response validation.
"""
from app.schemas.common import PaginatedResponse, ErrorResponse, SuccessResponse
from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentResponse,
)
from app.schemas.milestone import (
    MilestoneCreate,
    MilestoneResponse,
)
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleResponse,
)
from app.schemas.alert import (
    AlertResponse,
    AlertWithAnalysis,
    AlertFilters,
)

__all__ = [
    # Common
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    # Shipment
    "ShipmentCreate",
    "ShipmentUpdate",
    "ShipmentResponse",
    # Milestone
    "MilestoneCreate",
    "MilestoneResponse",
    # Schedule
    "ScheduleCreate",
    "ScheduleResponse",
    # Alert
    "AlertResponse",
    "AlertWithAnalysis",
    "AlertFilters",
]

# Made with Bob