"""
SLA Rule model - defines configurable SLA rules for detecting issues.
"""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import String, DateTime, Integer, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SLARule(Base):
    """
    SLA Rule model for defining conditions that trigger alerts.
    
    Rule Types:
    - MISSING_UPDATE: Milestone not received when expected
    - LATE_ARRIVAL: Milestone received but later than expected
    - STALE_STATUS: No updates for extended period
    - CUSTOMS_DELAY: Customs clearance taking too long
    - LOCATION_MISMATCH: Shipment at unexpected location
    """
    __tablename__ = "sla_rules"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Core fields
    rule_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )
    rule_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    milestone_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Rule configuration stored as JSON
    condition_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )
    
    # Threshold in minutes
    threshold_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    
    # Priority level for alerts triggered by this rule
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="MEDIUM"
    )
    
    # Active status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    # Description
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
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
    
    # Indexes
    __table_args__ = (
        Index("idx_sla_rule_type", "rule_type"),
        Index("idx_sla_rule_active", "is_active"),
        Index("idx_sla_rule_type_active", "rule_type", "is_active"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<SLARule(id={self.id}, name={self.rule_name}, "
            f"type={self.rule_type}, active={self.is_active})>"
        )

# Made with Bob
