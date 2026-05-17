"""Database models for SupBuddy logistics tracking system."""
from app.models.shipment import Shipment
from app.models.milestone import Milestone
from app.models.schedule import Schedule
from app.models.sla_rule import SLARule
from app.models.alert import Alert
from app.models.alert_analysis import AlertAnalysis

__all__ = [
    "Shipment",
    "Milestone",
    "Schedule",
    "SLARule",
    "Alert",
    "AlertAnalysis",
]

# Made with Bob
