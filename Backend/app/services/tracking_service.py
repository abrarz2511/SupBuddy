"""
Tracking service for shipment and milestone management.
"""
from datetime import datetime, timezone
from uuid import UUID
from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.shipment import Shipment
from app.models.milestone import Milestone
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate
from app.schemas.milestone import MilestoneCreate


class TrackingService:
    """Service for managing shipments and milestones."""

    @staticmethod
    async def create_shipment(
        data: ShipmentCreate, db: AsyncSession
    ) -> Shipment:
        """
        Create a new shipment.

        Args:
            data: Shipment creation data
            db: Database session

        Returns:
            Created shipment

        Raises:
            ValueError: If tracking number already exists
        """
        # Check if tracking number already exists
        result = await db.execute(
            select(Shipment).where(
                Shipment.tracking_number == data.tracking_number
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError(
                f"Shipment with tracking number {data.tracking_number} already exists"
            )

        # Create shipment
        shipment = Shipment(
            tracking_number=data.tracking_number,
            origin=data.origin,
            destination=data.destination,
            customer_id=data.customer_id,
            current_status="CREATED",
        )

        db.add(shipment)
        await db.flush()
        await db.refresh(shipment)

        return shipment

    @staticmethod
    async def get_shipment_by_tracking_number(
        tracking_number: str, db: AsyncSession, include_details: bool = False
    ) -> Optional[Shipment]:
        """
        Get shipment by tracking number.

        Args:
            tracking_number: Tracking number to search for
            db: Database session
            include_details: Whether to load milestones and schedules

        Returns:
            Shipment if found, None otherwise
        """
        query = select(Shipment).where(
            Shipment.tracking_number == tracking_number
        )

        if include_details:
            query = query.options(
                selectinload(Shipment.milestones),
                selectinload(Shipment.schedules),
                selectinload(Shipment.alerts),
            )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_shipment_by_id(
        shipment_id: UUID, db: AsyncSession, include_details: bool = False
    ) -> Optional[Shipment]:
        """
        Get shipment by ID.

        Args:
            shipment_id: Shipment UUID
            db: Database session
            include_details: Whether to load milestones and schedules

        Returns:
            Shipment if found, None otherwise
        """
        query = select(Shipment).where(Shipment.id == shipment_id)

        if include_details:
            query = query.options(
                selectinload(Shipment.milestones),
                selectinload(Shipment.schedules),
                selectinload(Shipment.alerts),
            )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_shipment(
        tracking_number: str, data: ShipmentUpdate, db: AsyncSession
    ) -> Optional[Shipment]:
        """
        Update shipment information.

        Args:
            tracking_number: Tracking number of shipment to update
            data: Update data
            db: Database session

        Returns:
            Updated shipment if found, None otherwise
        """
        shipment = await TrackingService.get_shipment_by_tracking_number(
            tracking_number, db
        )

        if not shipment:
            return None

        # Update fields if provided
        if data.origin is not None:
            shipment.origin = data.origin
        if data.destination is not None:
            shipment.destination = data.destination
        if data.customer_id is not None:
            shipment.customer_id = data.customer_id
        if data.current_status is not None:
            shipment.current_status = data.current_status
        if data.current_location is not None:
            shipment.current_location = data.current_location

        shipment.updated_at = datetime.now(timezone.utc)

        await db.flush()
        await db.refresh(shipment)

        return shipment

    @staticmethod
    async def add_milestone(
        shipment_id: UUID, data: MilestoneCreate, db: AsyncSession
    ) -> Milestone:
        """
        Add a milestone to a shipment.

        Args:
            shipment_id: Shipment UUID
            data: Milestone creation data
            db: Database session

        Returns:
            Created milestone

        Raises:
            ValueError: If shipment not found
        """
        # Verify shipment exists
        shipment = await TrackingService.get_shipment_by_id(shipment_id, db)
        if not shipment:
            raise ValueError(f"Shipment with ID {shipment_id} not found")

        # Create milestone
        milestone = Milestone(
            shipment_id=shipment_id,
            milestone_type=data.milestone_type,
            location=data.location,
            timestamp=data.timestamp,
            status=data.status,
            received=data.received,
            approved=data.approved,
            notes=data.notes,
        )

        db.add(milestone)

        # Update shipment status and location
        shipment.current_status = data.milestone_type
        shipment.current_location = data.location
        shipment.updated_at = datetime.now(timezone.utc)

        await db.flush()
        await db.refresh(milestone)

        return milestone

    @staticmethod
    async def get_shipment_milestones(
        shipment_id: UUID, db: AsyncSession
    ) -> List[Milestone]:
        """
        Get all milestones for a shipment, ordered by timestamp.

        Args:
            shipment_id: Shipment UUID
            db: Database session

        Returns:
            List of milestones
        """
        result = await db.execute(
            select(Milestone)
            .where(Milestone.shipment_id == shipment_id)
            .order_by(Milestone.timestamp.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_all_shipments(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Shipment], int]:
        """
        Get all shipments with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (shipments list, total count)
        """
        # Get total count
        count_result = await db.execute(select(func.count(Shipment.id)))
        total = count_result.scalar_one()

        # Get shipments
        result = await db.execute(
            select(Shipment)
            .order_by(Shipment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        shipments = list(result.scalars().all())

        return shipments, total

    @staticmethod
    async def get_active_shipments(db: AsyncSession) -> List[Shipment]:
        """
        Get all active shipments (not delivered or cancelled).

        Args:
            db: Database session

        Returns:
            List of active shipments
        """
        result = await db.execute(
            select(Shipment)
            .where(Shipment.current_status.notin_(["DELIVERED", "CANCELLED"]))
            .options(
                selectinload(Shipment.milestones),
                selectinload(Shipment.schedules),
            )
        )
        return list(result.scalars().all())


# Made with Bob
