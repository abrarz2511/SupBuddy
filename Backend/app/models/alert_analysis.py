"""
Alert Analysis model - stores AI agent analysis results for alerts.
"""
from datetime import datetime, timezone
from uuid import uuid4
from decimal import Decimal

from sqlalchemy import String, DateTime, Text, ForeignKey, Index, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AlertAnalysis(Base):
    """
    Alert Analysis model storing AI agent analysis results.
    
    Contains the Freight Exception Analyst Agent's analysis including:
    - Likely cause of the issue
    - Risk priority assessment
    - Confidence level in the analysis
    - Supporting evidence from external factors
    - Recommended actions to resolve the issue
    """
    __tablename__ = "alert_analyses"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Foreign key (one-to-one with Alert)
    alert_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("alerts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Analysis results
    likely_cause: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    risk_priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    confidence_level: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),  # e.g., 0.85 for 85% confidence
        nullable=False
    )
    
    # Supporting evidence stored as JSON
    supporting_evidence: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )
    
    
    # External factors considered (weather, traffic, etc.)
    external_factors: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Analysis metadata
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    agent_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Relationships
    alert: Mapped["Alert"] = relationship(
        "Alert",
        back_populates="analysis"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_analysis_alert", "alert_id"),
        Index("idx_analysis_analyzed_at", "analyzed_at"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<AlertAnalysis(id={self.id}, alert_id={self.alert_id}, "
            f"confidence={self.confidence_level})>"
        )

# Made with Bob
