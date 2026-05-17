"""
Shipment model - represents a shipment being tracked through the logistics network.
"""
from datetime import datetime, timezone
from typing import List
from uuid import uuid4

from sqlalchemy import String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Shipment(Base):
    """
    Shipment model representing a package being tracked through the logistics network.
    
    Tracks shipments from origin to destination through multiple milestones:
    Port → Customs → Delivery Center → Regional Hub → Customer
    """
    __tablename__ = "shipments"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Core fields
    tracking_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    origin: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    current_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        default="CREATED"
    )
    current_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    milestones: Mapped[List["Milestone"]] = relationship(
        "Milestone",
        back_populates="shipment",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    schedules: Mapped[List["Schedule"]] = relationship(
        "Schedule",
        back_populates="shipment",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert",
        back_populates="shipment",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_shipment_tracking", "tracking_number"),
        Index("idx_shipment_status", "current_status"),
        Index("idx_shipment_customer", "customer_id"),
        Index("idx_shipment_created", "created_at"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Shipment(id={self.id}, tracking_number={self.tracking_number}, "
            f"status={self.current_status})>"
        )

# Made with Bob
