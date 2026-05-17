"""
Shipments API endpoints for managing shipments and milestones.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.tracking_service import TrackingService
from app.schemas.shipment import (
    ShipmentCreate,
    ShipmentResponse,
    ShipmentUpdate,
)
from app.schemas.milestone import MilestoneCreate, MilestoneResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.post(
    "/",
    response_model=ShipmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new shipment",
    description="Create a new shipment."
)
async def create_shipment(
    data: ShipmentCreate,
    db: AsyncSession = Depends(get_db)
) -> ShipmentResponse:
    """Create a new shipment."""
    try:
        shipment = await TrackingService.create_shipment(data, db)
        await db.commit()
        return ShipmentResponse.model_validate(shipment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=PaginatedResponse[ShipmentResponse],
    summary="List all shipments",
    description="Get a paginated list of all shipments."
)
async def list_shipments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of items per page",
    ),
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[ShipmentResponse]:
    """List all shipments with pagination."""
    skip = (page - 1) * page_size
    shipments, total = await TrackingService.get_all_shipments(
        db,
        skip=skip,
        limit=page_size,
    )

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=[ShipmentResponse.model_validate(s) for s in shipments],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/active",
    response_model=List[ShipmentResponse],
    summary="List active shipments",
    description="Get all active shipments (not delivered or cancelled)."
)
async def list_active_shipments(
    db: AsyncSession = Depends(get_db)
) -> List[ShipmentResponse]:
    """List all active shipments."""
    shipments = await TrackingService.get_active_shipments(db)
    return [ShipmentResponse.model_validate(s) for s in shipments]


@router.get(
    "/tracking/{tracking_number}",
    response_model=ShipmentResponse,
    summary="Get shipment by tracking number",
    description="Get detailed shipment information by tracking number."
)
async def get_shipment_by_tracking(
    tracking_number: str,
    db: AsyncSession = Depends(get_db)
) -> ShipmentResponse:
    """Get shipment by tracking number with full details."""
    shipment = await TrackingService.get_shipment_by_tracking_number(
        tracking_number, db, include_details=True
    )

    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Shipment with tracking number {tracking_number} not found"
            ),
        )

    # Count active alerts
    active_statuses = {"OPEN", "ANALYZING", "ANALYZED"}
    alert_count = sum(
        1 for alert in shipment.alerts if alert.status in active_statuses
    )

    response = ShipmentResponse.model_validate(shipment)
    response.alert_count = alert_count
    return response


@router.get(
    "/{shipment_id}",
    response_model=ShipmentResponse,
    summary="Get shipment by ID",
    description="Get detailed shipment information by UUID."
)
async def get_shipment(
    shipment_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ShipmentResponse:
    """Get shipment by ID with full details."""
    shipment = await TrackingService.get_shipment_by_id(
        shipment_id, db, include_details=True
    )

    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with ID {shipment_id} not found"
        )

    # Count active alerts
    active_statuses = {"OPEN", "ANALYZING", "ANALYZED"}
    alert_count = sum(
        1 for alert in shipment.alerts if alert.status in active_statuses
    )

    response = ShipmentResponse.model_validate(shipment)
    response.alert_count = alert_count
    return response


@router.patch(
    "/tracking/{tracking_number}",
    response_model=ShipmentResponse,
    summary="Update shipment",
    description="Update shipment status and location by tracking number."
)
async def update_shipment(
    tracking_number: str,
    data: ShipmentUpdate,
    db: AsyncSession = Depends(get_db)
) -> ShipmentResponse:
    """Update shipment information."""
    shipment = await TrackingService.update_shipment(tracking_number, data, db)

    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with tracking number {tracking_number} not found"
        )

    await db.commit()
    return ShipmentResponse.model_validate(shipment)


@router.post(
    "/{shipment_id}/milestones",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add milestone to shipment",
    description="Add a new milestone event to a shipment."
)
async def add_milestone(
    shipment_id: UUID,
    data: MilestoneCreate,
    db: AsyncSession = Depends(get_db)
) -> MilestoneResponse:
    """Add a milestone to a shipment."""
    try:
        milestone = await TrackingService.add_milestone(shipment_id, data, db)
        await db.commit()
        return MilestoneResponse.model_validate(milestone)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/{shipment_id}/milestones",
    response_model=List[MilestoneResponse],
    summary="Get shipment milestones",
    description="Get all milestones for a shipment, ordered by timestamp."
)
async def get_shipment_milestones(
    shipment_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> List[MilestoneResponse]:
    """Get all milestones for a shipment."""
    milestones = await TrackingService.get_shipment_milestones(shipment_id, db)
    return [MilestoneResponse.model_validate(m) for m in milestones]


# Made with Bob
