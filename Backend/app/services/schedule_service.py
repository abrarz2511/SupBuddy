"""
Schedule service for managing shipment timelines and expected milestones.
"""
from datetime import datetime, timezone
from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schedule import Schedule
from app.models.shipment import Shipment
from app.schemas.schedule import ScheduleCreate


class ScheduleService:
    """Service for managing shipment schedules and timelines."""
    
    @staticmethod
    async def create_schedule(
        shipment_id: UUID,
        data: ScheduleCreate,
        db: AsyncSession
    ) -> Schedule:
        """
        Create a schedule entry for a shipment milestone.
        
        Args:
            shipment_id: Shipment UUID
            data: Schedule creation data
            db: Database session
            
        Returns:
            Created schedule
            
        Raises:
            ValueError: If shipment not found or duplicate schedule exists
        """
        # Verify shipment exists
        result = await db.execute(
            select(Shipment).where(Shipment.id == shipment_id)
        )
        shipment = result.scalar_one_or_none()
        if not shipment:
            raise ValueError(f"Shipment with ID {shipment_id} not found")
        
        # Check for duplicate schedule (same shipment + milestone type)
        existing_result = await db.execute(
            select(Schedule).where(
                Schedule.shipment_id == shipment_id,
                Schedule.milestone_type == data.milestone_type
            )
        )
        if existing_result.scalar_one_or_none():
            raise ValueError(
                f"Schedule for milestone type {data.milestone_type} already exists for this shipment"
            )
        
        # Create schedule
        schedule = Schedule(
            shipment_id=shipment_id,
            milestone_type=data.milestone_type,
            expected_location=data.expected_location,
            expected_arrival=data.expected_arrival,
            expected_departure=data.expected_departure,
            buffer_minutes=data.buffer_minutes,
        )
        
        db.add(schedule)
        await db.flush()
        await db.refresh(schedule)
        
        return schedule
    
    @staticmethod
    async def create_schedules_bulk(
        shipment_id: UUID,
        schedules_data: List[ScheduleCreate],
        db: AsyncSession
    ) -> List[Schedule]:
        """
        Create multiple schedule entries for a shipment.
        
        Args:
            shipment_id: Shipment UUID
            schedules_data: List of schedule creation data
            db: Database session
            
        Returns:
            List of created schedules
        """
        schedules = []
        for data in schedules_data:
            try:
                schedule = await ScheduleService.create_schedule(shipment_id, data, db)
                schedules.append(schedule)
            except ValueError:
                # Skip duplicates
                continue
        
        return schedules
    
    @staticmethod
    async def get_shipment_schedules(
        shipment_id: UUID,
        db: AsyncSession
    ) -> List[Schedule]:
        """
        Get all schedules for a shipment, ordered by expected arrival.
        
        Args:
            shipment_id: Shipment UUID
            db: Database session
            
        Returns:
            List of schedules
        """
        result = await db.execute(
            select(Schedule)
            .where(Schedule.shipment_id == shipment_id)
            .order_by(Schedule.expected_arrival.asc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_schedule_by_id(
        schedule_id: UUID,
        db: AsyncSession
    ) -> Optional[Schedule]:
        """
        Get schedule by ID.
        
        Args:
            schedule_id: Schedule UUID
            db: Database session
            
        Returns:
            Schedule if found, None otherwise
        """
        result = await db.execute(
            select(Schedule).where(Schedule.id == schedule_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def check_schedule_adherence(
        shipment_id: UUID,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Check if shipment is adhering to its schedule.
        
        Compares actual milestones against expected schedule to determine
        if shipment is on time, delayed, or ahead of schedule.
        
        Args:
            shipment_id: Shipment UUID
            db: Database session
            
        Returns:
            Dictionary with adherence status and details
        """
        # Get shipment with milestones and schedules
        result = await db.execute(
            select(Shipment).where(Shipment.id == shipment_id)
        )
        shipment = result.scalar_one_or_none()
        
        if not shipment:
            raise ValueError(f"Shipment with ID {shipment_id} not found")
        
        # Get schedules and milestones
        schedules = await ScheduleService.get_shipment_schedules(shipment_id, db)
        
        # Build milestone lookup by type
        milestone_map = {m.milestone_type: m for m in shipment.milestones}
        
        adherence_data = {
            "shipment_id": str(shipment_id),
            "tracking_number": shipment.tracking_number,
            "overall_status": "ON_TIME",
            "milestones": []
        }
        
        now = datetime.now(timezone.utc)
        has_delays = False
        
        for schedule in schedules:
            milestone = milestone_map.get(schedule.milestone_type)
            
            milestone_status = {
                "milestone_type": schedule.milestone_type,
                "expected_arrival": schedule.expected_arrival.isoformat(),
                "expected_location": schedule.expected_location,
                "status": "PENDING"
            }
            
            if milestone:
                # Milestone exists - check if on time
                milestone_status["actual_arrival"] = milestone.timestamp.isoformat()
                milestone_status["actual_location"] = milestone.location
                
                delay = (milestone.timestamp - schedule.expected_arrival).total_seconds() / 60
                milestone_status["delay_minutes"] = int(delay)
                
                if delay > schedule.buffer_minutes:
                    milestone_status["status"] = "DELAYED"
                    has_delays = True
                elif delay < -schedule.buffer_minutes:
                    milestone_status["status"] = "EARLY"
                else:
                    milestone_status["status"] = "ON_TIME"
            else:
                # Milestone not yet received
                if now > schedule.expected_arrival:
                    # Past expected time
                    delay = (now - schedule.expected_arrival).total_seconds() / 60
                    milestone_status["delay_minutes"] = int(delay)
                    
                    if delay > schedule.buffer_minutes:
                        milestone_status["status"] = "MISSING"
                        has_delays = True
                    else:
                        milestone_status["status"] = "PENDING"
                else:
                    milestone_status["status"] = "PENDING"
            
            adherence_data["milestones"].append(milestone_status)
        
        # Set overall status
        if has_delays:
            adherence_data["overall_status"] = "DELAYED"
        
        return adherence_data
    
    @staticmethod
    async def get_overdue_schedules(db: AsyncSession) -> List[Schedule]:
        """
        Get all schedules that are past their expected arrival time
        and don't have a corresponding milestone yet.
        
        Args:
            db: Database session
            
        Returns:
            List of overdue schedules
        """
        now = datetime.now(timezone.utc)
        
        result = await db.execute(
            select(Schedule)
            .where(Schedule.expected_arrival < now)
            .order_by(Schedule.expected_arrival.asc())
        )
        
        return list(result.scalars().all())


# Made with Bob