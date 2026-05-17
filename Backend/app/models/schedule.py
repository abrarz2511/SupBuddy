"""
Schedule model - stores predetermined expected timelines for shipments.
"""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import String, DateTime, Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Schedule(Base):
    """
    Schedule model representing expected timeline for shipment milestones.
    
    Stores predetermined schedule that the SLA engine will compare against
    to detect delays and issues.
    """
    __tablename__ = "schedules"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Foreign key
    shipment_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shipments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Core fields
    milestone_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    expected_location: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    expected_arrival: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    expected_departure: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Buffer time in minutes before triggering alert
    buffer_minutes: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False
    )
    
    # Audit timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    shipment: Mapped["Shipment"] = relationship(
        "Shipment",
        back_populates="schedules"
    )
    
    # Indexes and constraints
    __table_args__ = (
        Index("idx_schedule_shipment", "shipment_id"),
        Index("idx_schedule_arrival", "expected_arrival"),
        Index("idx_schedule_shipment_type", "shipment_id", "milestone_type"),
        # Ensure one schedule per milestone type per shipment
        UniqueConstraint("shipment_id", "milestone_type", name="uq_shipment_milestone"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Schedule(id={self.id}, shipment_id={self.shipment_id}, "
            f"type={self.milestone_type}, expected={self.expected_arrival})>"
        )

# Made with Bob
