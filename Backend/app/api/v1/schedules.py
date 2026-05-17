"""
Schedules API endpoints for managing shipment schedules and timelines.
"""
from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.schedule_service import ScheduleService
from app.schemas.schedule import ScheduleCreate, ScheduleResponse

router = APIRouter()


@router.post(
    "/shipments/{shipment_id}/schedules",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create schedule for shipment",
    description="Create a new schedule entry for a shipment milestone."
)
async def create_schedule(
    shipment_id: UUID,
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db)
) -> ScheduleResponse:
    """Create a schedule entry for a shipment."""
    try:
        schedule = await ScheduleService.create_schedule(shipment_id, data, db)
        await db.commit()
        return ScheduleResponse.model_validate(schedule)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/shipments/{shipment_id}/schedules/bulk",
    response_model=List[ScheduleResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple schedules",
    description="Create multiple schedule entries for a shipment in bulk."
)
async def create_schedules_bulk(
    shipment_id: UUID,
    schedules_data: List[ScheduleCreate],
    db: AsyncSession = Depends(get_db)
) -> List[ScheduleResponse]:
    """Create multiple schedule entries for a shipment."""
    try:
        schedules = await ScheduleService.create_schedules_bulk(
            shipment_id, schedules_data, db
        )
        await db.commit()
        return [ScheduleResponse.model_validate(s) for s in schedules]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/shipments/{shipment_id}/schedules",
    response_model=List[ScheduleResponse],
    summary="Get shipment schedules",
    description="Get all schedule entries for a shipment."
)
async def get_shipment_schedules(
    shipment_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> List[ScheduleResponse]:
    """Get all schedules for a shipment."""
    schedules = await ScheduleService.get_shipment_schedules(shipment_id, db)
    return [ScheduleResponse.model_validate(s) for s in schedules]


@router.get(
    "/schedules/overdue",
    response_model=List[ScheduleResponse],
    summary="Get overdue schedules",
    description="Get schedules past their expected arrival time."
)
async def get_overdue_schedules(
    db: AsyncSession = Depends(get_db)
) -> List[ScheduleResponse]:
    """Get all overdue schedules."""
    schedules = await ScheduleService.get_overdue_schedules(db)
    return [ScheduleResponse.model_validate(s) for s in schedules]


@router.get(
    "/schedules/{schedule_id}",
    response_model=ScheduleResponse,
    summary="Get schedule by ID",
    description="Get a specific schedule entry by its UUID."
)
async def get_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ScheduleResponse:
    """Get schedule by ID."""
    schedule = await ScheduleService.get_schedule_by_id(schedule_id, db)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with ID {schedule_id} not found"
        )

    return ScheduleResponse.model_validate(schedule)


@router.get(
    "/shipments/{shipment_id}/schedules/adherence",
    response_model=Dict[str, Any],
    summary="Check schedule adherence",
    description="Check whether a shipment is adhering to its schedule."
)
async def check_schedule_adherence(
    shipment_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Check schedule adherence for a shipment."""
    try:
        adherence = await ScheduleService.check_schedule_adherence(
            shipment_id,
            db,
        )
        return adherence
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Made with Bob
