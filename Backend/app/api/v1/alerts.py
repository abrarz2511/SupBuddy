"""
Alerts API endpoints for managing alerts and AI analysis.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.alert_service import AlertService
from app.schemas.alert import AlertResponse, AlertWithAnalysis
from app.schemas.common import SuccessResponse

router = APIRouter()


@router.get(
    "/",
    response_model=List[AlertResponse],
    summary="List alerts",
    description="Get a list of alerts with optional filters."
)
async def list_alerts(
    shipment_id: Optional[UUID] = Query(
        None,
        description="Filter by shipment ID",
    ),
    status: Optional[str] = Query(
        None,
        description="Filter by status",
    ),
    priority: Optional[str] = Query(
        None,
        description="Filter by priority",
    ),
    alert_type: Optional[str] = Query(
        None,
        description="Filter by alert type",
    ),
    from_date: Optional[datetime] = Query(
        None,
        description="Filter alerts detected after this date",
    ),
    to_date: Optional[datetime] = Query(
        None,
        description="Filter alerts detected before this date",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of results",
    ),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    include_analysis: bool = Query(
        False,
        description="Include AI analysis in response",
    ),
    db: AsyncSession = Depends(get_db)
) -> List[AlertResponse]:
    """List alerts with optional filters."""
    alert_service = AlertService()

    alerts = await alert_service.list_alerts(
        db=db,
        shipment_id=shipment_id,
        status=status,
        priority=priority,
        alert_type=alert_type,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
        include_analysis=include_analysis
    )

    return [AlertResponse.model_validate(a) for a in alerts]


@router.post(
    "/analyze-pending",
    response_model=SuccessResponse,
    summary="Analyze pending alerts in batch",
    description="Trigger AI analysis for pending alerts in batch."
)
async def analyze_pending_alerts(
    max_alerts: int = Query(
        10,
        ge=1,
        le=50,
        description="Maximum number of alerts to analyze",
    ),
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """Analyze multiple pending alerts in batch."""
    alert_service = AlertService()

    try:
        analyses = await alert_service.analyze_pending_alerts(
            db,
            max_alerts=max_alerts,
        )

        return SuccessResponse(
            message=f"Successfully analyzed {len(analyses)} alerts",
            data={
                "analyzed_count": len(analyses),
                "alert_ids": [str(a.alert_id) for a in analyses]
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze pending alerts: {str(e)}"
        )


@router.get(
    "/{alert_id}",
    response_model=AlertWithAnalysis,
    summary="Get alert by ID",
    description="Get detailed alert information by UUID."
)
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> AlertWithAnalysis:
    """Get alert by ID with analysis."""
    alert_service = AlertService()
    alert = await alert_service.get_alert_by_id(
        alert_id,
        db,
        include_analysis=True,
    )

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )

    return AlertWithAnalysis.model_validate(alert)


@router.post(
    "/{alert_id}/analyze",
    response_model=AlertWithAnalysis,
    summary="Analyze alert with AI",
    description="Trigger AI agent analysis for an alert."
)
async def analyze_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> AlertWithAnalysis:
    """Analyze an alert using AI agent."""
    alert_service = AlertService()

    try:
        await alert_service.analyze_alert(alert_id, db)

        # Fetch updated alert with analysis
        alert = await alert_service.get_alert_by_id(
            alert_id,
            db,
            include_analysis=True,
        )

        return AlertWithAnalysis.model_validate(alert)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze alert: {str(e)}"
        )


@router.patch(
    "/{alert_id}/status",
    response_model=AlertResponse,
    summary="Update alert status",
    description="Update the status of an alert."
)
async def update_alert_status(
    alert_id: UUID,
    new_status: str = Query(..., description="New status"),
    resolved_at: Optional[datetime] = Query(
        None,
        description="Resolution timestamp",
    ),
    db: AsyncSession = Depends(get_db)
) -> AlertResponse:
    """Update alert status."""
    alert_service = AlertService()

    try:
        alert = await alert_service.update_alert_status(
            alert_id=alert_id,
            status=new_status,
            db=db,
            resolved_at=resolved_at
        )

        return AlertResponse.model_validate(alert)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/statistics/summary",
    response_model=Dict[str, Any],
    summary="Get alert statistics",
    description="Get statistical summary of alerts."
)
async def get_alert_statistics(
    shipment_id: Optional[UUID] = Query(
        None,
        description="Filter by shipment ID",
    ),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get alert statistics."""
    alert_service = AlertService()

    stats = await alert_service.get_alert_statistics(
        db,
        shipment_id=shipment_id,
    )

    return stats


@router.get(
    "/shipments/{shipment_id}/alerts",
    response_model=List[AlertWithAnalysis],
    summary="Get alerts for shipment",
    description="Get all alerts for a specific shipment."
)
async def get_shipment_alerts(
    shipment_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> List[AlertWithAnalysis]:
    """Get all alerts for a shipment."""
    alert_service = AlertService()

    alerts = await alert_service.list_alerts(
        db=db,
        shipment_id=shipment_id,
        include_analysis=True
    )

    return [AlertWithAnalysis.model_validate(a) for a in alerts]


# Made with Bob
