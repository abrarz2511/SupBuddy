"""
Shipment Pydantic schemas for API validation.
"""
from datetime import datetime
from uuid import UUID
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class ShipmentCreate(BaseModel):
    """Schema for creating a new shipment."""
    
    tracking_number: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Unique tracking number"
    )
    origin: str = Field(..., min_length=1, max_length=255, description="Origin location")
    destination: str = Field(..., min_length=1, max_length=255, description="Destination location")
    customer_id: str | None = Field(None, max_length=100, description="Customer identifier")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tracking_number": "SHIP-2024-001234",
                "origin": "Shanghai Port, China",
                "destination": "Los Angeles Port, USA",
                "customer_id": "CUST-5678"
            }
        }
    )


class ShipmentUpdate(BaseModel):
    """Schema for updating shipment information."""
    
    origin: str | None = Field(None, min_length=1, max_length=255, description="Origin location")
    destination: str | None = Field(None, min_length=1, max_length=255, description="Destination location")
    customer_id: str | None = Field(None, max_length=100, description="Customer identifier")
    current_status: str | None = Field(None, max_length=50, description="Current shipment status")
    current_location: str | None = Field(None, max_length=255, description="Current location")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "origin": "Shanghai Port, China",
                "destination": "Los Angeles Port, USA",
                "customer_id": "CUST-5678",
                "current_status": "CUSTOMS_CLEARED",
                "current_location": "Los Angeles Port, USA"
            }
        }
    )


class ShipmentResponse(BaseModel):
    """
    Schema for shipment response with optional nested data.
    
    When used in list endpoints, milestones/schedules will be empty.
    When used in detail endpoints, they will be populated.
    """
    
    id: UUID = Field(..., description="Shipment unique identifier")
    tracking_number: str = Field(..., description="Tracking number")
    origin: str = Field(..., description="Origin location")
    destination: str = Field(..., description="Destination location")
    current_status: str = Field(..., description="Current status")
    current_location: str | None = Field(None, description="Current location")
    customer_id: str | None = Field(None, description="Customer identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Optional nested data - populated only when explicitly loaded
    milestones: List["MilestoneResponse"] = Field(
        default_factory=list,
        description="Shipment milestones (populated in detail view)"
    )
    schedules: List["ScheduleResponse"] = Field(
        default_factory=list,
        description="Expected schedules (populated in detail view)"
    )
    alert_count: int = Field(
        default=0,
        description="Number of active alerts"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "tracking_number": "SHIP-2024-001234",
                "origin": "Shanghai Port, China",
                "destination": "Los Angeles Port, USA",
                "current_status": "IN_TRANSIT",
                "current_location": "Singapore Hub",
                "customer_id": "CUST-5678",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-16T14:20:00Z",
                "milestones": [],
                "schedules": [],
                "alert_count": 0
            }
        }
    )


# Import here to avoid circular dependency
from app.schemas.milestone import MilestoneResponse  # noqa: E402
from app.schemas.schedule import ScheduleResponse  # noqa: E402

# Update forward references
ShipmentResponse.model_rebuild()


# Made with Bob
