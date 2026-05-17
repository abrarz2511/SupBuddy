"""
API v1 package initialization.
"""
from fastapi import APIRouter
from app.api.v1 import shipments, schedules, alerts

# Create main v1 router
router = APIRouter()

# Include all sub-routers
router.include_router(
    shipments.router,
    prefix="/shipments",
    tags=["Shipments"]
)

router.include_router(
    schedules.router,
    prefix="/schedules",
    tags=["Schedules"]
)

router.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["Alerts"]
)

# Made with Bob
