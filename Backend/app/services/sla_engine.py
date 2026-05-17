"""
SLA Engine service for evaluating shipments against SLA rules.
"""
import yaml
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shipment import Shipment
from app.models.milestone import Milestone
from app.models.schedule import Schedule
from app.models.alert import Alert


class SLAEngine:
    """
    SLA Engine for evaluating shipments against configured rules.

    Loads rules from YAML configuration and checks shipments for violations.
    """

    def __init__(self, rules_path: str = "app/config/sla_rules.yaml"):
        """
        Initialize SLA Engine with rules from configuration file.

        Args:
            rules_path: Path to SLA rules YAML file
        """
        self.rules_path = rules_path
        self.rules = self._load_rules()

    def _load_rules(self) -> List[Dict[str, Any]]:
        """
        Load SLA rules from YAML configuration file.

        Returns:
            List of rule dictionaries
        """
        rules_file = Path(self.rules_path)
        if not rules_file.exists():
            raise FileNotFoundError(
                f"SLA rules file not found: {self.rules_path}"
            )

        with open(rules_file, "r") as f:
            config = yaml.safe_load(f)

        return config.get("rules", [])

    def get_rules_by_type(self, rule_type: str) -> List[Dict[str, Any]]:
        """
        Get all rules of a specific type.

        Args:
            rule_type: Type of rule (MISSING_UPDATE, LATE_ARRIVAL, etc.)

        Returns:
            List of matching rules
        """
        return [rule for rule in self.rules if rule.get("type") == rule_type]

    async def evaluate_all_shipments(self, db: AsyncSession) -> List[Alert]:
        """
        Evaluate all active shipments against SLA rules.

        Args:
            db: Database session

        Returns:
            List of newly created alerts
        """
        # Get all active shipments
        result = await db.execute(
            select(Shipment).where(
                Shipment.current_status.notin_(["DELIVERED", "CANCELLED"])
            )
        )
        shipments = result.scalars().all()

        all_alerts = []
        for shipment in shipments:
            alerts = await self.evaluate_shipment(shipment.id, db)
            all_alerts.extend(alerts)

        return all_alerts

    async def evaluate_shipment(
        self, shipment_id: UUID, db: AsyncSession
    ) -> List[Alert]:
        """
        Evaluate a single shipment against all SLA rules.

        Args:
            shipment_id: Shipment UUID
            db: Database session

        Returns:
            List of newly created alerts
        """
        # Get shipment with related data
        result = await db.execute(
            select(Shipment).where(Shipment.id == shipment_id)
        )
        shipment = result.scalar_one_or_none()

        if not shipment:
            return []

        # Get schedules and milestones
        schedules_result = await db.execute(
            select(Schedule).where(Schedule.shipment_id == shipment_id)
        )
        schedules = list(schedules_result.scalars().all())

        milestones_result = await db.execute(
            select(Milestone).where(Milestone.shipment_id == shipment_id)
        )
        milestones = list(milestones_result.scalars().all())

        # Build milestone lookup
        milestone_map = {m.milestone_type: m for m in milestones}

        alerts = []

        # Check missing updates
        missing_alerts = await self._check_missing_updates(
            shipment, schedules, milestone_map, db
        )
        alerts.extend(missing_alerts)

        # Check late arrivals
        late_alerts = await self._check_late_arrivals(
            shipment, schedules, milestone_map, db
        )
        alerts.extend(late_alerts)

        # Check customs delays
        customs_alerts = await self._check_customs_delays(
            shipment, milestones, db
        )
        alerts.extend(customs_alerts)

        # Check stale status
        stale_alert = await self._check_stale_status(shipment, milestones, db)
        if stale_alert:
            alerts.append(stale_alert)

        return alerts

    async def _check_missing_updates(
        self,
        shipment: Shipment,
        schedules: List[Schedule],
        milestone_map: Dict[str, Milestone],
        db: AsyncSession,
    ) -> List[Alert]:
        """Check for missing milestone updates."""
        alerts = []
        now = datetime.now(timezone.utc)

        rules = self.get_rules_by_type("MISSING_UPDATE")

        for schedule in schedules:
            # Skip if milestone already received
            if schedule.milestone_type in milestone_map:
                continue

            # Check if past expected time + buffer
            time_since_expected = (
                now - schedule.expected_arrival
            ).total_seconds() / 60

            # Find matching rule
            matching_rule = next(
                (
                    r
                    for r in rules
                    if r.get("milestone_type") == schedule.milestone_type
                ),
                None,
            )

            if not matching_rule:
                continue

            threshold = matching_rule["threshold_minutes"]

            if time_since_expected > (schedule.buffer_minutes + threshold):
                # Check if alert already exists
                existing = await self._alert_exists(
                    shipment.id, "MISSING_UPDATE", schedule.milestone_type, db
                )

                if not existing:
                    alert = Alert(
                        shipment_id=shipment.id,
                        alert_type="MISSING_UPDATE",
                        priority=matching_rule["priority"],
                        status="OPEN",
                        backend_reason=matching_rule["description"],
                        milestone_type=schedule.milestone_type,
                        expected_time=schedule.expected_arrival,
                        delay_minutes=int(time_since_expected),
                    )
                    db.add(alert)
                    await db.flush()
                    await db.refresh(alert)
                    alerts.append(alert)

        return alerts

    async def _check_late_arrivals(
        self,
        shipment: Shipment,
        schedules: List[Schedule],
        milestone_map: Dict[str, Milestone],
        db: AsyncSession,
    ) -> List[Alert]:
        """Check for late milestone arrivals."""
        alerts = []
        rules = self.get_rules_by_type("LATE_ARRIVAL")

        for schedule in schedules:
            milestone = milestone_map.get(schedule.milestone_type)
            if not milestone:
                continue

            # Calculate delay
            delay_minutes = (
                milestone.timestamp - schedule.expected_arrival
            ).total_seconds() / 60

            # Find matching rule
            matching_rule = next(
                (
                    r
                    for r in rules
                    if r.get("milestone_type") == schedule.milestone_type
                ),
                None,
            )

            if not matching_rule:
                continue

            threshold = matching_rule["threshold_minutes"]

            if delay_minutes > threshold:
                # Check if alert already exists
                existing = await self._alert_exists(
                    shipment.id, "LATE_ARRIVAL", schedule.milestone_type, db
                )

                if not existing:
                    alert = Alert(
                        shipment_id=shipment.id,
                        alert_type="LATE_ARRIVAL",
                        priority=matching_rule["priority"],
                        status="OPEN",
                        backend_reason=matching_rule["description"],
                        milestone_type=schedule.milestone_type,
                        expected_time=schedule.expected_arrival,
                        actual_time=milestone.timestamp,
                        delay_minutes=int(delay_minutes),
                    )
                    db.add(alert)
                    await db.flush()
                    await db.refresh(alert)
                    alerts.append(alert)

        return alerts

    async def _check_customs_delays(
        self, shipment: Shipment, milestones: List[Milestone], db: AsyncSession
    ) -> List[Alert]:
        """Check for customs processing delays."""
        alerts = []
        rules = self.get_rules_by_type("CUSTOMS_DELAY")

        # Find customs milestones
        customs_submitted = next(
            (m for m in milestones if m.milestone_type == "CUSTOMS_SUBMITTED"),
            None,
        )
        customs_cleared = next(
            (m for m in milestones if m.milestone_type == "CUSTOMS_CLEARED"),
            None,
        )

        if customs_submitted and not customs_cleared:
            # Still in customs - check how long
            now = datetime.now(timezone.utc)
            time_in_customs = (
                now - customs_submitted.timestamp
            ).total_seconds() / 60

            for rule in rules:
                threshold = rule["threshold_minutes"]

                if time_in_customs > threshold:
                    # Check if alert already exists
                    existing = await self._alert_exists(
                        shipment.id, "CUSTOMS_DELAY", "CUSTOMS_CLEARED", db
                    )

                    if not existing:
                        alert = Alert(
                            shipment_id=shipment.id,
                            alert_type="CUSTOMS_DELAY",
                            priority=rule["priority"],
                            status="OPEN",
                            backend_reason=rule["description"],
                            milestone_type="CUSTOMS_CLEARED",
                            expected_time=customs_submitted.timestamp
                            + timedelta(minutes=threshold),
                            delay_minutes=int(time_in_customs),
                        )
                        db.add(alert)
                        await db.flush()
                        await db.refresh(alert)
                        alerts.append(alert)
                        break  # Only create one customs delay alert

        return alerts

    async def _check_stale_status(
        self, shipment: Shipment, milestones: List[Milestone], db: AsyncSession
    ) -> Optional[Alert]:
        """Check for stale status (no updates for extended period)."""
        if not milestones:
            return None

        # Get most recent milestone
        latest_milestone = max(milestones, key=lambda m: m.timestamp)
        now = datetime.now(timezone.utc)
        time_since_update = (
            now - latest_milestone.timestamp
        ).total_seconds() / 60

        rules = self.get_rules_by_type("STALE_STATUS")

        # Find the highest threshold that's been exceeded
        applicable_rule = None
        for rule in sorted(
            rules, key=lambda r: r["threshold_minutes"], reverse=True
        ):
            if time_since_update > rule["threshold_minutes"]:
                applicable_rule = rule
                break

        if applicable_rule:
            # Check if alert already exists
            existing = await self._alert_exists(
                shipment.id, "STALE_STATUS", None, db
            )

            if not existing:
                alert = Alert(
                    shipment_id=shipment.id,
                    alert_type="STALE_STATUS",
                    priority=applicable_rule["priority"],
                    status="OPEN",
                    backend_reason=applicable_rule["description"],
                    delay_minutes=int(time_since_update),
                )
                db.add(alert)
                await db.flush()
                await db.refresh(alert)
                return alert

        return None

    async def _alert_exists(
        self,
        shipment_id: UUID,
        alert_type: str,
        milestone_type: Optional[str],
        db: AsyncSession,
    ) -> bool:
        """
        Check if an alert already exists for this shipment/type/milestone.

        Only checks for open or analyzing alerts to avoid duplicates.
        """
        query = select(Alert).where(
            Alert.shipment_id == shipment_id,
            Alert.alert_type == alert_type,
            Alert.status.in_(["OPEN", "ANALYZING"]),
        )

        if milestone_type:
            query = query.where(Alert.milestone_type == milestone_type)

        result = await db.execute(query)
        return result.scalar_one_or_none() is not None


# Made with Bob
