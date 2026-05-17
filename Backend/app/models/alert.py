"""
Alert model - stores detected SLA violations and exceptions.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Alert(Base):
    """
    Alert model representing detected SLA violations and exceptions.
    
    Alert Status:
    - OPEN: Newly detected, awaiting analysis
    - ANALYZING: Sent to agent for analysis
    - ANALYZED: Agent analysis complete
    - RESOLVED: Issue resolved
    - CLOSED: Alert closed without resolution
    
    Priority Levels:
    - LOW: Minor delay within acceptable range
    - MEDIUM: Moderate delay requiring attention
    - HIGH: Significant delay impacting delivery
    - CRITICAL: Severe issue requiring immediate action
    """
    __tablename__ = "alerts"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Foreign keys
    shipment_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shipments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sla_rule_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sla_rules.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Core fields
    alert_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="OPEN",
        index=True
    )
    
    # Timestamps
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Backend rule reason
    backend_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    
    # Milestone information
    milestone_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    expected_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    actual_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    delay_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    # Audit timestamps
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
    shipment: Mapped["Shipment"] = relationship(
        "Shipment",
        back_populates="alerts"
    )
    sla_rule: Mapped[Optional["SLARule"]] = relationship(
        "SLARule"
    )
    analysis: Mapped[Optional["AlertAnalysis"]] = relationship(
        "AlertAnalysis",
        back_populates="alert",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_alert_shipment", "shipment_id"),
        Index("idx_alert_status", "status"),
        Index("idx_alert_priority", "priority"),
        Index("idx_alert_detected", "detected_at"),
        Index("idx_alert_status_priority", "status", "priority"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Alert(id={self.id}, type={self.alert_type}, "
            f"priority={self.priority}, status={self.status})>"
        )

# Made with Bob
