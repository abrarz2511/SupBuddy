"""
Weather data context tool.

Fetches weather information from NOAA Weather.gov API to help analyze
shipment delays caused by weather conditions.
"""
import httpx
from typing import Dict, Any, List, Tuple


async def get_weather_data(location: str) -> Dict[str, Any]:
    """
    Get weather data for a location using NOAA Weather.gov API.

    The Weather.gov API requires coordinates (lat/lon). If a location name
    is provided, it should be converted to coordinates first.

    Args:
        location: Location string (coordinates as "lat,lon" or location name)

    Returns:
        Dictionary with weather information:
            - description: str (e.g., "Clear", "Rainy", "Storm")
            - severity: str ("low", "medium", "high")
            - temperature: float (in Celsius)
            - conditions: list of current conditions
            - alerts: list of weather alerts
    """
    try:
        # Parse coordinates from location
        lat, lon = _parse_location(location)

        # Get weather data from Weather.gov API
        weather_data = await _fetch_weather_gov_data(lat, lon)

        return weather_data

    except Exception as e:
        # Return fallback data if API fails
        return {
            "description": "Weather data unavailable",
            "severity": "unknown",
            "temperature": 0,
            "wind_speed": 0,
            "humidity": 0,
            "conditions": ["Unknown"],
            "alerts": [],
            "error": str(e),
        }


def _parse_location(location: str) -> Tuple[float, float]:
    """
    Parse location string to extract coordinates.

    Args:
        location: Location string (e.g., "40.7128,-74.0060" or city name)

    Returns:
        Tuple of (latitude, longitude)

    Raises:
        ValueError: If location cannot be parsed
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

    # Default coordinates for common ports (fallback)
    # In production, use a geocoding service to convert names to coordinates
    port_coordinates = {
        "shanghai": (31.2304, 121.4737),
        "los angeles": (33.7405, -118.2713),
        "singapore": (1.2644, 103.8220),
        "rotterdam": (51.9244, 4.4777),
        "hong kong": (22.3193, 114.1694),
        "new york": (40.7128, -74.0060),
    }

    location_lower = location.lower()
    for port_name, coords in port_coordinates.items():
        if port_name in location_lower:
            return coords

    # Default to New York if location not recognized
    return 40.7128, -74.0060


async def _fetch_weather_gov_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch weather data from NOAA Weather.gov API.

    API Documentation: https://www.weather.gov/documentation/services-web-api

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Dictionary with weather information
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Step 1: Get grid point data for the coordinates
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        headers = {
            # Weather.gov requires a descriptive User-Agent.
            "User-Agent": "(SupBuddy Logistics, contact@supbuddy.com)",
            "Accept": "application/geo+json",
        }

        points_response = await client.get(points_url, headers=headers)
        points_response.raise_for_status()
        points_data = points_response.json()

        # Extract forecast URLs
        properties = points_data.get("properties", {})
        forecast_url = properties.get("forecast")
        # Step 2: Get current forecast
        forecast_response = await client.get(forecast_url, headers=headers)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        # Step 3: Get active weather alerts for the area
        alerts_url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"
        alerts_response = await client.get(alerts_url, headers=headers)
        alerts_response.raise_for_status()
        alerts_data = alerts_response.json()

        # Parse forecast data
        periods = forecast_data.get("properties", {}).get("periods", [])
        current_period = periods[0] if periods else {}

        # Parse alerts
        alert_features = alerts_data.get("features", [])
        alerts = []
        for alert in alert_features:
            alert_props = alert.get("properties", {})
            alerts.append(
                {
                    "event": alert_props.get("event", ""),
                    "severity": alert_props.get("severity", ""),
                    "headline": alert_props.get("headline", ""),
                    "description": alert_props.get("description", ""),
                }
            )

        # Extract weather information
        description = current_period.get("shortForecast", "Unknown")
        temperature_f = current_period.get("temperature", 0)
        temperature_c = (temperature_f - 32) * 5 / 9  # Convert F to C
        wind_speed = current_period.get("windSpeed", "0 mph")

        # Determine severity
        severity = _determine_weather_severity(description, alerts)

        return {
            "description": description,
            "severity": severity,
            "temperature": round(temperature_c, 1),
            "temperature_f": temperature_f,
            "wind_speed": wind_speed,
            "humidity": current_period.get("relativeHumidity", {}).get(
                "value", 0
            ),
            "conditions": [description],
            "alerts": alerts,
            "detailed_forecast": current_period.get("detailedForecast", ""),
        }


def _determine_weather_severity(
    condition_text: str,
    alerts: List[Dict[str, Any]] | None = None,
) -> str:
    """
    Determine weather severity based on condition description and alerts.

    Args:
        condition_text: Weather condition description
        alerts: List of weather alerts (optional)

    Returns:
        Severity level: "low", "medium", or "high"
    """
    # Check alerts first - they indicate high severity
    if alerts:
        for alert in alerts:
            severity = alert.get("severity", "").lower()
            if severity in ["extreme", "severe"]:
                return "high"
            elif severity in ["moderate"]:
                return "medium"

    condition_lower = condition_text.lower()

    # High severity conditions
    high_severity = [
        "storm",
        "hurricane",
        "typhoon",
        "tornado",
        "blizzard",
        "severe",
        "heavy rain",
        "heavy snow",
        "flooding",
        "ice",
    ]

    # Medium severity conditions
    medium_severity = [
        "rain",
        "snow",
        "thunderstorm",
        "fog",
        "wind",
        "cloudy",
        "overcast",
        "drizzle",
    ]

    for term in high_severity:
        if term in condition_lower:
            return "high"

    for term in medium_severity:
        if term in condition_lower:
            return "medium"

    return "low"


# Made with Bob
