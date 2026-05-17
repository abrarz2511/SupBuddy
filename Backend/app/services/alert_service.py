"""
Alert Service for managing alerts and AI agent analysis.

Orchestrates the complete alert analysis workflow:
1. Collect external context data
2. Call AI agent for analysis
3. Store analysis results in database
"""
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alert import Alert
from app.models.alert_analysis import AlertAnalysis
from app.models.shipment import Shipment
from app.services.agent_gateway import AgentGateway
from app.services.context_service import ContextService

logger = logging.getLogger(__name__)


class AlertService:
    """
    Service for managing alerts and coordinating AI agent analysis.

    Handles the complete workflow from alert creation through agent analysis
    and result storage.
    """

    def __init__(
        self,
        agent_gateway: Optional[AgentGateway] = None,
        context_service: Optional[ContextService] = None,
    ):
        """
        Initialize alert service.

        Args:
            agent_gateway: Gateway for AI agent communication (creates default if None)
            context_service: Service for context collection (creates default if None)
        """
        self.agent_gateway = agent_gateway or AgentGateway()
        self.context_service = context_service or ContextService()

    async def get_alert_by_id(
        self, alert_id: UUID, db: AsyncSession, include_analysis: bool = True
    ) -> Optional[Alert]:
        """
        Get alert by ID with optional analysis.

        Args:
            alert_id: Alert UUID
            db: Database session
            include_analysis: Whether to include analysis relationship

        Returns:
            Alert or None if not found
        """
        query = select(Alert).where(Alert.id == alert_id)

        if include_analysis:
            query = query.options(selectinload(Alert.analysis))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def list_alerts(
        self,
        db: AsyncSession,
        shipment_id: Optional[UUID] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        alert_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        include_analysis: bool = False,
    ) -> List[Alert]:
        """
        List alerts with optional filters.

        Args:
            db: Database session
            shipment_id: Filter by shipment ID
            status: Filter by status
            priority: Filter by priority
            alert_type: Filter by alert type
            from_date: Filter alerts detected after this date
            to_date: Filter alerts detected before this date
            limit: Maximum number of results
            offset: Number of results to skip
            include_analysis: Whether to include analysis relationship

        Returns:
            List of alerts
        """
        query = select(Alert)

        # Apply filters
        conditions = []
        if shipment_id:
            conditions.append(Alert.shipment_id == shipment_id)
        if status:
            conditions.append(Alert.status == status)
        if priority:
            conditions.append(Alert.priority == priority)
        if alert_type:
            conditions.append(Alert.alert_type == alert_type)
        if from_date:
            conditions.append(Alert.detected_at >= from_date)
        if to_date:
            conditions.append(Alert.detected_at <= to_date)

        if conditions:
            query = query.where(and_(*conditions))

        # Include analysis if requested
        if include_analysis:
            query = query.options(selectinload(Alert.analysis))

        # Order by detected_at descending (newest first)
        query = query.order_by(Alert.detected_at.desc())

        # Apply pagination
        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def analyze_alert(
        self, alert_id: UUID, db: AsyncSession
    ) -> AlertAnalysis:
        """
        Analyze an alert using AI agent with context collection.

        Complete workflow:
        1. Fetch alert and shipment data
        2. Update alert status to ANALYZING
        3. Collect external context data
        4. Call AI agent for analysis
        5. Store analysis results
        6. Update alert status to ANALYZED

        Args:
            alert_id: Alert UUID to analyze
            db: Database session

        Returns:
            Created AlertAnalysis object

        Raises:
            ValueError: If alert not found or already analyzed
            Exception: If analysis fails
        """
        logger.info(f"Starting analysis for alert {alert_id}")

        # Fetch alert with shipment
        result = await db.execute(
            select(Alert)
            .where(Alert.id == alert_id)
            .options(selectinload(Alert.shipment))
        )
        alert = result.scalar_one_or_none()

        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        # Check if already analyzed
        if alert.analysis:
            raise ValueError(f"Alert {alert_id} already has analysis")

        # Get shipment
        shipment = alert.shipment
        if not shipment:
            raise ValueError(f"Shipment not found for alert {alert_id}")

        try:
            # Update alert status to ANALYZING
            alert.status = "ANALYZING"
            await db.commit()
            await db.refresh(alert)

            logger.info(f"Collecting context for alert {alert_id}")

            # Collect external context
            context = await self.context_service.collect_context(
                alert, shipment
            )

            logger.info(
                f"Context collected: {len(context.get('collection_metadata', {}).get('tools_succeeded', []))} "
                f"tools succeeded"
            )

            # Call AI agent for analysis
            logger.info(f"Calling AI agent for alert {alert_id}")
            analysis_result = await self.agent_gateway.analyze_alert(
                alert, shipment, context
            )

            logger.info(f"AI agent analysis complete for alert {alert_id}")

            # Create analysis record
            analysis = AlertAnalysis(
                alert_id=alert.id,
                likely_cause=analysis_result["likely_cause"],
                risk_priority=analysis_result["risk_priority"],
                confidence_level=analysis_result["confidence_level"],
                supporting_evidence=analysis_result.get("supporting_evidence"),
                external_factors=analysis_result.get("external_factors"),
                agent_version=self.agent_gateway.agent_version,
            )

            db.add(analysis)

            # Update alert status to ANALYZED
            alert.status = "ANALYZED"

            # Commit all changes
            await db.commit()
            await db.refresh(analysis)
            await db.refresh(alert)

            logger.info(
                f"Analysis complete for alert {alert_id}: "
                f"cause='{analysis.likely_cause[:50]}...', "
                f"priority={analysis.risk_priority}, "
                f"confidence={analysis.confidence_level}"
            )

            return analysis

        except Exception as e:
            # Rollback on error
            await db.rollback()

            # Update alert status back to OPEN
            alert.status = "OPEN"
            await db.commit()

            logger.error(
                f"Failed to analyze alert {alert_id}: {e}", exc_info=True
            )
            raise

    async def analyze_pending_alerts(
        self, db: AsyncSession, max_alerts: int = 10
    ) -> List[AlertAnalysis]:
        """
        Analyze multiple pending alerts in batch.

        Processes alerts with status OPEN, up to max_alerts limit.
        Useful for scheduled batch processing.

        Args:
            db: Database session
            max_alerts: Maximum number of alerts to process

        Returns:
            List of created AlertAnalysis objects
        """
        logger.info(f"Starting batch analysis for up to {max_alerts} alerts")

        # Get pending alerts
        result = await db.execute(
            select(Alert)
            .where(Alert.status == "OPEN")
            .order_by(Alert.priority.desc(), Alert.detected_at.asc())
            .limit(max_alerts)
        )
        pending_alerts = list(result.scalars().all())

        if not pending_alerts:
            logger.info("No pending alerts to analyze")
            return []

        logger.info(f"Found {len(pending_alerts)} pending alerts")

        analyses = []
        for alert in pending_alerts:
            try:
                analysis = await self.analyze_alert(alert.id, db)
                analyses.append(analysis)
            except Exception as e:
                logger.error(
                    f"Failed to analyze alert {alert.id} in batch: {e}",
                    exc_info=True,
                )
                # Continue with next alert
                continue

        logger.info(
            f"Batch analysis complete: {len(analyses)}/{len(pending_alerts)} succeeded"
        )

        return analyses

    async def update_alert_status(
        self,
        alert_id: UUID,
        status: str,
        db: AsyncSession,
        resolved_at: Optional[datetime] = None,
    ) -> Alert:
        """
        Update alert status.

        Args:
            alert_id: Alert UUID
            status: New status (OPEN, ANALYZING, ANALYZED, RESOLVED, CLOSED)
            db: Database session
            resolved_at: Resolution timestamp (for RESOLVED status)

        Returns:
            Updated alert

        Raises:
            ValueError: If alert not found or invalid status
        """
        valid_statuses = [
            "OPEN",
            "ANALYZING",
            "ANALYZED",
            "RESOLVED",
            "CLOSED",
        ]
        if status not in valid_statuses:
            raise ValueError(
                f"Invalid status: {status}. Must be one of {valid_statuses}"
            )

        alert = await self.get_alert_by_id(
            alert_id, db, include_analysis=False
        )
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        alert.status = status

        if status == "RESOLVED" and resolved_at:
            alert.resolved_at = resolved_at
        elif status == "RESOLVED" and not resolved_at:
            alert.resolved_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(alert)

        logger.info(f"Updated alert {alert_id} status to {status}")

        return alert

    async def get_alert_statistics(
        self, db: AsyncSession, shipment_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get alert statistics.

        Args:
            db: Database session
            shipment_id: Optional shipment ID to filter by

        Returns:
            Dictionary with statistics:
                - total_alerts: int
                - by_status: Dict[str, int]
                - by_priority: Dict[str, int]
                - by_type: Dict[str, int]
                - analyzed_count: int
                - average_confidence: float (if analyses exist)
        """
        from sqlalchemy import func

        # Base query
        query = select(Alert)
        if shipment_id:
            query = query.where(Alert.shipment_id == shipment_id)

        result = await db.execute(query)
        alerts = list(result.scalars().all())

        if not alerts:
            return {
                "total_alerts": 0,
                "by_status": {},
                "by_priority": {},
                "by_type": {},
                "analyzed_count": 0,
            }

        # Calculate statistics
        by_status = {}
        by_priority = {}
        by_type = {}

        for alert in alerts:
            by_status[alert.status] = by_status.get(alert.status, 0) + 1
            by_priority[alert.priority] = (
                by_priority.get(alert.priority, 0) + 1
            )
            by_type[alert.alert_type] = by_type.get(alert.alert_type, 0) + 1

        # Get analysis statistics
        analysis_query = select(AlertAnalysis)
        if shipment_id:
            analysis_query = analysis_query.join(Alert).where(
                Alert.shipment_id == shipment_id
            )

        analysis_result = await db.execute(analysis_query)
        analyses = list(analysis_result.scalars().all())

        stats = {
            "total_alerts": len(alerts),
            "by_status": by_status,
            "by_priority": by_priority,
            "by_type": by_type,
            "analyzed_count": len(analyses),
        }

        if analyses:
            avg_confidence = sum(
                float(a.confidence_level) for a in analyses
            ) / len(analyses)
            stats["average_confidence"] = round(avg_confidence, 2)

        return stats


# Made with Bob
