"""
Traffic data context tool.

Fetches traffic and route information using TomTom Routing API
to help analyze shipment delays caused by road congestion or route issues.
"""
import httpx
from typing import Dict, Any, Tuple

from app.config import settings


async def get_traffic_data(origin: str, destination: str) -> Dict[str, Any]:
    """
    Get traffic data for a route using TomTom Routing API.

    Args:
        origin: Starting location.
        destination: Ending location.

    Returns:
        Dictionary with traffic information:
            - status: str ("clear", "moderate", "heavy", "blocked")
            - delay_minutes: int (traffic delay in minutes)
            - distance_km: float (route distance)
            - travel_time_minutes: int (estimated travel time with traffic)
            - incidents: list of traffic incidents
    """
    try:
        # Parse coordinates from location strings
        origin_lat, origin_lon = _parse_location(origin)
        dest_lat, dest_lon = _parse_location(destination)

        # Get route data from TomTom API
        route_data = await _fetch_tomtom_route(
            origin_lat, origin_lon, dest_lat, dest_lon
        )

        return route_data

    except Exception as e:
        # Return fallback data if API fails
        return {
            "status": "unknown",
            "delay_minutes": 0,
            "distance_km": 0,
            "travel_time_minutes": 0,
            "incidents": [],
            "error": str(e),
        }


def _parse_location(location: str) -> Tuple[float, float]:
    """
    Parse location string to extract coordinates.

    Args:
        location: Location string (e.g., "40.7128,-74.0060" or city name)

    Returns:
        Tuple of (latitude, longitude)
    """
    # Try to parse as coordinates
    if "," in location:
        try:
            parts = location.split(",")
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            return lat, lon
        except (ValueError, IndexError):
            pass

    # Default coordinates for common ports/cities (fallback)
    # In production, use TomTom Geocoding API to convert names to coordinates
    location_coordinates = {
        "shanghai": (31.2304, 121.4737),
        "los angeles": (33.7405, -118.2713),
        "singapore": (1.2644, 103.8220),
        "rotterdam": (51.9244, 4.4777),
        "hong kong": (22.3193, 114.1694),
        "new york": (40.7128, -74.0060),
        "london": (51.5074, -0.1278),
        "tokyo": (35.6762, 139.6503),
    }

    location_lower = location.lower()
    for name, coords in location_coordinates.items():
        if name in location_lower:
            return coords

    # Default to New York if location not recognized
    return 40.7128, -74.0060


async def _fetch_tomtom_route(
    origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float
) -> Dict[str, Any]:
    """
    Fetch route data from TomTom Routing API.

    API Documentation: https://developer.tomtom.com/routing-api/documentation

    Args:
        origin_lat: Origin latitude
        origin_lon: Origin longitude
        dest_lat: Destination latitude
        dest_lon: Destination longitude

    Returns:
        Dictionary with traffic and route information
    """
    # Build TomTom Routing API URL
    locations = f"{origin_lat},{origin_lon}:{dest_lat},{dest_lon}"
    api_url = (
        f"https://api.tomtom.com/routing/1/calculateRoute/{locations}/json"
    )

    params = {
        "key": settings.traffic_api_key,
        "traffic": "true",  # Include traffic data
        "travelMode": "truck",  # Use truck mode for logistics
        "routeType": "fastest",  # Get fastest route
        "computeTravelTimeFor": "all",  # Get all travel time variants
    }

    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(api_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Parse TomTom response
        routes = data.get("routes", [])
        if not routes:
            raise ValueError("No routes found in TomTom response")

        # Get first (best) route
        route = routes[0]
        summary = route.get("summary", {})

        # Extract route information
        travel_time_seconds = summary.get("travelTimeInSeconds", 0)
        traffic_delay_seconds = summary.get("trafficDelayInSeconds", 0)
        length_meters = summary.get("lengthInMeters", 0)

        # Convert to more useful units
        travel_time_minutes = travel_time_seconds // 60
        delay_minutes = traffic_delay_seconds // 60
        distance_km = length_meters / 1000

        # Determine traffic status based on delay
        status = _determine_traffic_status_from_delay(
            delay_minutes, travel_time_minutes
        )

        # Extract incidents if available
        incidents = []
        legs = route.get("legs", [])
        for leg in legs:
            for point in leg.get("points", []):
                if "trafficIncident" in point:
                    incidents.append(
                        {
                            "type": point["trafficIncident"].get(
                                "type", "unknown"
                            ),
                            "description": point["trafficIncident"].get(
                                "description", ""
                            ),
                            "delay": point["trafficIncident"].get("delay", 0),
                        }
                    )

        return {
            "status": status,
            "delay_minutes": int(delay_minutes),
            "distance_km": round(distance_km, 2),
            "travel_time_minutes": int(travel_time_minutes),
            "travel_time_no_traffic_minutes": int(
                (travel_time_seconds - traffic_delay_seconds) // 60
            ),
            "incidents": incidents[:5],  # Limit to top 5 incidents
            "route_available": True,
        }


def _determine_traffic_status_from_delay(
    delay_minutes: int, total_travel_minutes: int
) -> str:
    """
    Determine traffic status based on delay relative to travel time.

    Args:
        delay_minutes: Traffic delay in minutes
        total_travel_minutes: Total travel time in minutes

    Returns:
        Traffic status: "clear", "moderate", "heavy", or "blocked"
    """
    if total_travel_minutes == 0:
        return "unknown"

    # Calculate delay percentage
    delay_percentage = (delay_minutes / total_travel_minutes) * 100

    if delay_percentage < 10:
        return "clear"
    elif delay_percentage < 25:
        return "moderate"
    elif delay_percentage < 50:
        return "heavy"
    else:
        return "blocked"


# Made with Bob
