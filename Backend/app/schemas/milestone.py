"""
Milestone Pydantic schemas for API validation.
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class MilestoneCreate(BaseModel):
    """Schema for creating a new milestone."""
    
    milestone_type: str = Field(
        ...,
        max_length=50,
        description="Type of milestone (PORT_RECEIVED, CUSTOMS_CLEARED, etc.)"
    )
    location: str = Field(..., min_length=1, max_length=255, description="Milestone location")
    timestamp: datetime = Field(..., description="When the milestone occurred")
    status: str = Field(default="PENDING", max_length=50, description="Milestone status")
    received: bool = Field(default=False, description="Whether milestone was received")
    approved: bool = Field(default=False, description="Whether milestone was approved")
    notes: str | None = Field(None, description="Additional notes")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "milestone_type": "PORT_RECEIVED",
                "location": "Shanghai Port, China",
                "timestamp": "2024-01-15T08:30:00Z",
                "status": "COMPLETED",
                "received": True,
                "approved": True,
                "notes": "Container received and inspected"
            }
        }
    )


class MilestoneResponse(BaseModel):
    """Schema for milestone response."""
    
    id: UUID = Field(..., description="Milestone unique identifier")
    shipment_id: UUID = Field(..., description="Associated shipment ID")
    milestone_type: str = Field(..., description="Type of milestone")
    location: str = Field(..., description="Milestone location")
    status: str = Field(..., description="Milestone status")
    received: bool = Field(..., description="Whether milestone was received")
    approved: bool = Field(..., description="Whether milestone was approved")
    timestamp: datetime = Field(..., description="When the milestone occurred")
    notes: str | None = Field(None, description="Additional notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "223e4567-e89b-12d3-a456-426614174001",
                "shipment_id": "123e4567-e89b-12d3-a456-426614174000",
                "milestone_type": "PORT_RECEIVED",
                "location": "Shanghai Port, China",
                "status": "COMPLETED",
                "received": True,
                "approved": True,
                "timestamp": "2024-01-15T08:30:00Z",
                "notes": "Container received and inspected",
                "created_at": "2024-01-15T08:35:00Z"
            }
        }
    )


# Made with Bob