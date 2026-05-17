"""
Schedule Pydantic schemas for API validation.
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ScheduleCreate(BaseModel):
    """Schema for creating a new schedule entry."""
    
    milestone_type: str = Field(
        ...,
        max_length=50,
        description="Type of milestone this schedule is for"
    )
    expected_location: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Expected location for this milestone"
    )
    expected_arrival: datetime = Field(..., description="Expected arrival time")
    expected_departure: datetime | None = Field(None, description="Expected departure time")
    buffer_minutes: int = Field(
        default=60,
        ge=0,
        description="Buffer time in minutes before triggering alert"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "milestone_type": "PORT_RECEIVED",
                "expected_location": "Shanghai Port, China",
                "expected_arrival": "2024-01-15T08:00:00Z",
                "expected_departure": "2024-01-15T18:00:00Z",
                "buffer_minutes": 120
            }
        }
    )


class ScheduleResponse(BaseModel):
    """Schema for schedule response."""
    
    id: UUID = Field(..., description="Schedule unique identifier")
    shipment_id: UUID = Field(..., description="Associated shipment ID")
    milestone_type: str = Field(..., description="Type of milestone")
    expected_location: str = Field(..., description="Expected location")
    expected_arrival: datetime = Field(..., description="Expected arrival time")
    expected_departure: datetime | None = Field(None, description="Expected departure time")
    buffer_minutes: int = Field(..., description="Buffer time in minutes")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "323e4567-e89b-12d3-a456-426614174002",
                "shipment_id": "123e4567-e89b-12d3-a456-426614174000",
                "milestone_type": "PORT_RECEIVED",
                "expected_location": "Shanghai Port, China",
                "expected_arrival": "2024-01-15T08:00:00Z",
                "expected_departure": "2024-01-15T18:00:00Z",
                "buffer_minutes": 120,
                "created_at": "2024-01-14T10:00:00Z"
            }
        }
    )


# Made with Bob