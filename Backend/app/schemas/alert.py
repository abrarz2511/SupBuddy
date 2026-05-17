"""
Alert Pydantic schemas for API validation.
"""
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any


class AlertFilters(BaseModel):
    """Schema for filtering alerts in list endpoints."""
    
    status: str | None = Field(None, description="Filter by status (OPEN, ANALYZING, ANALYZED, etc.)")
    priority: str | None = Field(None, description="Filter by priority (LOW, MEDIUM, HIGH, CRITICAL)")
    alert_type: str | None = Field(None, description="Filter by alert type")
    shipment_id: UUID | None = Field(None, description="Filter by shipment ID")
    from_date: datetime | None = Field(None, description="Filter alerts detected after this date")
    to_date: datetime | None = Field(None, description="Filter alerts detected before this date")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "OPEN",
                "priority": "HIGH",
                "from_date": "2024-01-01T00:00:00Z"
            }
        }
    )


class AlertAnalysisResponse(BaseModel):
    """Schema for alert analysis response (standalone or nested)."""
    
    id: UUID = Field(..., description="Analysis unique identifier")
    alert_id: UUID = Field(..., description="Associated alert ID")
    likely_cause: str = Field(..., description="AI-determined likely cause")
    risk_priority: str = Field(..., description="Risk priority assessment")
    confidence_level: Decimal = Field(..., description="Confidence level (0.00-1.00)")
    supporting_evidence: Dict[str, Any] | None = Field(None, description="Supporting evidence")
    external_factors: Dict[str, Any] | None = Field(None, description="External factors considered")
    analyzed_at: datetime = Field(..., description="Analysis timestamp")
    agent_version: str | None = Field(None, description="Agent version used")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "523e4567-e89b-12d3-a456-426614174004",
                "alert_id": "423e4567-e89b-12d3-a456-426614174003",
                "likely_cause": "Port congestion due to severe weather conditions",
                "risk_priority": "HIGH",
                "confidence_level": "0.87",
                "supporting_evidence": {
                    "weather": "Typhoon warning in effect",
                    "port_status": "Operations suspended"
                },
                "external_factors": {
                    "weather_severity": "high",
                    "estimated_delay": "24-48 hours"
                },
                "analyzed_at": "2024-01-16T10:15:00Z",
                "agent_version": "1.0.0"
            }
        }
    )


class AlertResponse(BaseModel):
    """Schema for alert response (basic alert data)."""
    
    id: UUID = Field(..., description="Alert unique identifier")
    shipment_id: UUID = Field(..., description="Associated shipment ID")
    sla_rule_id: UUID | None = Field(None, description="SLA rule that triggered this alert")
    alert_type: str = Field(..., description="Type of alert")
    priority: str = Field(..., description="Alert priority")
    status: str = Field(..., description="Alert status")
    detected_at: datetime = Field(..., description="When alert was detected")
    resolved_at: datetime | None = Field(None, description="When alert was resolved")
    backend_reason: str | None = Field(None, description="Backend-generated reason")
    milestone_type: str | None = Field(None, description="Related milestone type")
    expected_time: datetime | None = Field(None, description="Expected time")
    actual_time: datetime | None = Field(None, description="Actual time")
    delay_minutes: int | None = Field(None, description="Delay in minutes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "423e4567-e89b-12d3-a456-426614174003",
                "shipment_id": "123e4567-e89b-12d3-a456-426614174000",
                "sla_rule_id": "623e4567-e89b-12d3-a456-426614174005",
                "alert_type": "MISSING_UPDATE",
                "priority": "HIGH",
                "status": "OPEN",
                "detected_at": "2024-01-16T10:00:00Z",
                "resolved_at": None,
                "backend_reason": "Expected PORT_RECEIVED milestone not received within 2 hours of scheduled time",
                "milestone_type": "PORT_RECEIVED",
                "expected_time": "2024-01-15T08:00:00Z",
                "actual_time": None,
                "delay_minutes": 120,
                "created_at": "2024-01-16T10:00:00Z",
                "updated_at": "2024-01-16T10:00:00Z"
            }
        }
    )


class AlertWithAnalysis(AlertResponse):
    """Schema for alert with AI analysis included (for detail views)."""
    
    analysis: AlertAnalysisResponse | None = Field(None, description="AI analysis if available")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "423e4567-e89b-12d3-a456-426614174003",
                "shipment_id": "123e4567-e89b-12d3-a456-426614174000",
                "alert_type": "MISSING_UPDATE",
                "priority": "HIGH",
                "status": "ANALYZED",
                "detected_at": "2024-01-16T10:00:00Z",
                "analysis": {
                    "likely_cause": "Port congestion",
                    "risk_priority": "HIGH",
                    "confidence_level": "0.87"
                }
            }
        }
    )


# Made with Bob