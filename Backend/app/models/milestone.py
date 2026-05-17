"""
Milestone model - tracks each checkpoint in the shipment journey.
"""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import String, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Milestone(Base):
    """
    Milestone model representing checkpoints in the shipment journey.
    
    Milestone Types:
    - PORT_RECEIVED: Shipment received at port
    - CUSTOMS_SUBMITTED: Submitted to customs
    - CUSTOMS_CLEARED: Cleared by customs
    - DELIVERY_CENTER_RECEIVED: Received at delivery center
    - REGIONAL_HUB_RECEIVED: Received at regional hub
    - OUT_FOR_DELIVERY: Out for final delivery
    - DELIVERED: Delivered to customer
    """
    __tablename__ = "milestones"
    
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
        nullable=False,
        index=True
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING"
    )
    
    # Status flags
    received: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    
    # Additional info
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Audit timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    shipment: Mapped["Shipment"] = relationship(
        "Shipment",
        back_populates="milestones"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_milestone_shipment", "shipment_id"),
        Index("idx_milestone_type", "milestone_type"),
        Index("idx_milestone_timestamp", "timestamp"),
        Index("idx_milestone_shipment_type", "shipment_id", "milestone_type"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Milestone(id={self.id}, type={self.milestone_type}, "
            f"location={self.location}, received={self.received})>"
        )

# Made with Bob
