"""
Context Service for collecting external context data before agent analysis.

This service intelligently collects weather, traffic, port status, and news data
based on alert type and shipment information, then provides it to the AI agent
for comprehensive analysis.
"""
import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Set, Optional, Tuple, Callable

from app.config import settings
from app.models.alert import Alert
from app.models.shipment import Shipment
from app.context_tools import (
    get_weather_data,
    get_traffic_data,
    get_port_status,
    get_relevant_news
)

logger = logging.getLogger(__name__)


# Context collection rules based on alert type
CONTEXT_RULES = {
    "DELAY_AT_PORT": {
        "weather": True,      # Check weather at port
        "traffic": False,     # Not relevant for port delays
        "port_status": True,  # Critical - check port operations
        "news": True,         # Check for port-related news
    },
    "DELAY_IN_TRANSIT": {
        "weather": True,      # Check weather along route
        "traffic": True,      # Check traffic conditions
        "port_status": False, # Not at port yet
        "news": True,         # Check for route disruptions
    },
    "CUSTOMS_DELAY": {
        "weather": False,     # Weather not relevant
        "traffic": False,     # Traffic not relevant
        "port_status": True,  # Port customs operations
        "news": True,         # Check for customs issues
    },
    "WEATHER_DELAY": {
        "weather": True,      # Primary context
        "traffic": True,      # Weather affects traffic
        "port_status": False, # Less relevant
        "news": True,         # Weather-related news
    },
    "GENERAL_DELAY": {
        "weather": True,      # Collect all context
        "traffic": True,      # for comprehensive analysis
        "port_status": True,
        "news": True,
    },
}


class ContextService:
    """
    Service for collecting external context data to support AI agent analysis.
    
    Intelligently determines which context to collect based on alert type,
    executes collection in parallel with retry logic, and handles partial
    failures gracefully.
    """
    
    def __init__(
        self,
        collection_timeout: Optional[int] = None,
        tool_timeout: Optional[int] = None,
        retry_enabled: Optional[bool] = None,
        max_retries: Optional[int] = None,
        parallel_execution: Optional[bool] = None
    ):
        """
        Initialize context service.
        
        Args:
            collection_timeout: Overall timeout for context collection (seconds).
                               Defaults to settings.context_collection_timeout
            tool_timeout: Timeout per individual tool (seconds).
                         Defaults to settings.context_tool_timeout
            retry_enabled: Whether to retry failed tools.
                          Defaults to settings.context_retry_enabled
            max_retries: Maximum number of retries per tool.
                        Defaults to settings.context_max_retries
            parallel_execution: Whether to execute tools in parallel.
                               Defaults to settings.context_parallel_execution
        """
        self.collection_timeout = collection_timeout or settings.context_collection_timeout
        self.tool_timeout = tool_timeout or settings.context_tool_timeout
        self.retry_enabled = retry_enabled if retry_enabled is not None else settings.context_retry_enabled
        self.max_retries = max_retries if max_retries is not None else settings.context_max_retries
        self.parallel_execution = parallel_execution if parallel_execution is not None else settings.context_parallel_execution
    
    async def collect_context(
        self,
        alert: Alert,
        shipment: Shipment
    ) -> Dict[str, Any]:
        """
        Collect all relevant context for alert analysis.
        
        Intelligently determines which context tools to call based on alert type,
        executes them in parallel, and handles failures gracefully.
        
        Args:
            alert: Alert to collect context for
            shipment: Associated shipment
            
        Returns:
            Dictionary with context data:
                - weather: Optional[Dict] - Weather data for relevant locations
                - traffic: Optional[Dict] - Traffic data for routes
                - port_status: Optional[Dict] - Port operational status
                - news: Optional[Dict] - Relevant news articles
                - collection_metadata: Dict - Collection statistics and errors
        """
        logger.info(
            f"Collecting context for alert {alert.id} "
            f"(type: {alert.alert_type}, shipment: {shipment.tracking_number})"
        )
        
        # Determine which context to collect
        required_tools = self._determine_required_context(alert, shipment)
        logger.info(f"Required context tools: {required_tools}")
        
        # Extract locations for context collection
        locations = self._extract_locations(alert, shipment)
        logger.debug(f"Extracted locations: {locations}")
        
        # Prepare collection tasks
        tasks = {}
        
        if "weather" in required_tools and locations["weather_locations"]:
            tasks["weather"] = self._collect_weather_context(
                locations["weather_locations"]
            )
        
        if "traffic" in required_tools and locations["traffic_routes"]:
            tasks["traffic"] = self._collect_traffic_context(
                locations["traffic_routes"]
            )
        
        if "port_status" in required_tools and locations["port_locations"]:
            tasks["port_status"] = self._collect_port_context(
                locations["port_locations"]
            )
        
        if "news" in required_tools and locations["news_locations"]:
            tasks["news"] = self._collect_news_context(
                locations["news_locations"],
                alert.alert_type
            )
        
        if not tasks:
            logger.warning("No context tasks to execute")
            return self._create_empty_context()
        
        # Execute collection with timeout
        start_time = time.time()
        
        try:
            if self.parallel_execution:
                # Execute all tasks in parallel
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks.values(), return_exceptions=True),
                    timeout=self.collection_timeout
                )
            else:
                # Execute sequentially (for debugging)
                results = []
                for task in tasks.values():
                    try:
                        result = await asyncio.wait_for(
                            task,
                            timeout=self.tool_timeout
                        )
                        results.append(result)
                    except Exception as e:
                        results.append(e)
        except asyncio.TimeoutError:
            logger.error(
                f"Context collection timed out after {self.collection_timeout}s"
            )
            return self._create_timeout_context(required_tools)
        
        collection_time = (time.time() - start_time) * 1000
        
        # Process results
        context = self._process_results(
            list(tasks.keys()),
            results,
            required_tools,
            collection_time
        )
        
        logger.info(
            f"Context collection complete: "
            f"{len(context['collection_metadata']['tools_succeeded'])} succeeded, "
            f"{len(context['collection_metadata']['tools_failed'])} failed, "
            f"time: {collection_time:.0f}ms"
        )
        
        return context
    
    def _determine_required_context(
        self,
        alert: Alert,
        shipment: Shipment
    ) -> Set[str]:
        """
        Intelligently determine which context to collect.
        
        Uses alert type to determine relevant context tools.
        
        Args:
            alert: Alert being analyzed
            shipment: Associated shipment
            
        Returns:
            Set of context types: {"weather", "traffic", "port_status", "news"}
        """
        alert_type = alert.alert_type
        
        # Get rules for this alert type, or use GENERAL_DELAY as fallback
        rules = CONTEXT_RULES.get(alert_type, CONTEXT_RULES["GENERAL_DELAY"])
        
        # Build set of required tools
        required = set()
        for tool, should_collect in rules.items():
            if should_collect:
                required.add(tool)
        
        return required
    
    def _extract_locations(
        self,
        alert: Alert,
        shipment: Shipment
    ) -> Dict[str, Any]:
        """
        Extract relevant locations for context collection.
        
        Args:
            alert: Alert being analyzed
            shipment: Associated shipment
            
        Returns:
            Dictionary with location lists:
                - weather_locations: List[str]
                - traffic_routes: List[Tuple[str, str]]
                - port_locations: List[str]
                - news_locations: List[str]
        """
        locations = {
            "weather_locations": [],
            "traffic_routes": [],
            "port_locations": [],
            "news_locations": []
        }
        
        # Extract from shipment
        if shipment.origin:
            locations["weather_locations"].append(shipment.origin)
            locations["news_locations"].append(shipment.origin)
        
        if shipment.destination:
            locations["weather_locations"].append(shipment.destination)
            locations["news_locations"].append(shipment.destination)
        
        if shipment.current_location:
            locations["weather_locations"].append(shipment.current_location)
            locations["news_locations"].append(shipment.current_location)
        
        # Traffic route
        if shipment.origin and shipment.destination:
            locations["traffic_routes"].append(
                (shipment.origin, shipment.destination)
            )
        
        # Extract port names from locations
        for loc in [shipment.origin, shipment.destination, shipment.current_location]:
            if loc and self._is_port_location(loc):
                locations["port_locations"].append(loc)
        
        # Deduplicate
        locations["weather_locations"] = list(set(locations["weather_locations"]))
        locations["news_locations"] = list(set(locations["news_locations"]))
        locations["port_locations"] = list(set(locations["port_locations"]))
        
        return locations
    
    def _is_port_location(self, location: str) -> bool:
        """Check if a location string represents a port."""
        if not location:
            return False
        
        location_lower = location.lower()
        port_indicators = ["port", "terminal", "harbor", "harbour", "seaport"]
        
        return any(indicator in location_lower for indicator in port_indicators)
    
    async def _collect_weather_context(
        self,
        locations: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Collect weather data for multiple locations.
        
        Args:
            locations: List of location strings
            
        Returns:
            Dictionary mapping location names to weather data
        """
        if not locations:
            return None
        
        weather_data = {}
        
        for location in locations[:3]:  # Limit to 3 locations
            try:
                data = await self._retry_with_backoff(
                    get_weather_data,
                    location
                )
                if data:
                    # Use simplified location name as key
                    key = self._simplify_location_name(location)
                    weather_data[key] = data
            except Exception as e:
                logger.error(f"Failed to get weather for {location}: {e}")
        
        return weather_data if weather_data else None
    
    async def _collect_traffic_context(
        self,
        routes: List[Tuple[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Collect traffic data for routes.
        
        Args:
            routes: List of (origin, destination) tuples
            
        Returns:
            Dictionary mapping route names to traffic data
        """
        if not routes:
            return None
        
        traffic_data = {}
        
        for origin, destination in routes[:2]:  # Limit to 2 routes
            try:
                data = await self._retry_with_backoff(
                    get_traffic_data,
                    origin,
                    destination
                )
                if data:
                    key = f"{self._simplify_location_name(origin)}_to_{self._simplify_location_name(destination)}"
                    traffic_data[key] = data
            except Exception as e:
                logger.error(f"Failed to get traffic for {origin} -> {destination}: {e}")
        
        return traffic_data if traffic_data else None
    
    async def _collect_port_context(
        self,
        port_locations: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Collect port status data.
        
        Args:
            port_locations: List of port location strings
            
        Returns:
            Dictionary mapping port names to status data
        """
        if not port_locations:
            return None
        
        port_data = {}
        
        for port in port_locations[:3]:  # Limit to 3 ports
            try:
                data = await self._retry_with_backoff(
                    get_port_status,
                    port,
                    days_back=7
                )
                if data:
                    key = self._simplify_location_name(port)
                    port_data[key] = data
            except Exception as e:
                logger.error(f"Failed to get port status for {port}: {e}")
        
        return port_data if port_data else None
    
    async def _collect_news_context(
        self,
        locations: List[str],
        alert_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Collect relevant news for locations.
        
        Args:
            locations: List of location strings
            alert_type: Type of alert (used to determine relevant keywords)
            
        Returns:
            Dictionary mapping location names to news data
        """
        if not locations:
            return None
        
        news_data = {}
        
        # Determine relevant keywords based on alert type
        keywords = self._get_news_keywords(alert_type)
        
        for location in locations[:3]:  # Limit to 3 locations
            try:
                data = await self._retry_with_backoff(
                    get_relevant_news,
                    location,
                    keywords,
                    days_back=7
                )
                if data:
                    key = self._simplify_location_name(location)
                    news_data[key] = data
            except Exception as e:
                logger.error(f"Failed to get news for {location}: {e}")
        
        return news_data if news_data else None
    
    def _get_news_keywords(self, alert_type: str) -> List[str]:
        """Get relevant news keywords based on alert type."""
        base_keywords = ["port", "shipping", "logistics", "delay"]
        
        type_specific = {
            "DELAY_AT_PORT": ["congestion", "strike", "customs"],
            "CUSTOMS_DELAY": ["customs", "inspection", "regulation"],
            "WEATHER_DELAY": ["storm", "weather", "flood", "hurricane"],
            "DELAY_IN_TRANSIT": ["traffic", "road closure", "accident"],
        }
        
        specific = type_specific.get(alert_type, [])
        return base_keywords + specific
    
    def _simplify_location_name(self, location: str) -> str:
        """Simplify location name for use as dictionary key."""
        # Remove common prefixes/suffixes
        simplified = location.lower()
        simplified = simplified.replace("port of ", "")
        simplified = simplified.replace(" port", "")
        simplified = simplified.replace(" terminal", "")
        simplified = simplified.strip()
        
        # Replace spaces with underscores
        simplified = simplified.replace(" ", "_")
        
        return simplified
    
    async def _retry_with_backoff(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Execute function with exponential backoff retry.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result or None if all retries failed
        """
        if not self.retry_enabled:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.tool_timeout
                )
            except Exception as e:
                logger.error(f"Failed to execute {func.__name__}: {e}")
                return None
        
        last_error = None
        initial_delay = 1.0
        
        for attempt in range(self.max_retries + 1):
            try:
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.tool_timeout
                )
                
                # Log success after retry
                if attempt > 0:
                    logger.info(
                        f"Succeeded on retry {attempt} for {func.__name__}"
                    )
                
                return result
                
            except Exception as e:
                last_error = e
                
                if attempt < self.max_retries:
                    delay = initial_delay * (2 ** attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_retries + 1} attempts failed for "
                        f"{func.__name__}: {e}"
                    )
        
        return None
    
    def _process_results(
        self,
        tool_names: List[str],
        results: List[Any],
        required_tools: Set[str],
        collection_time: float
    ) -> Dict[str, Any]:
        """
        Process collection results and build context dictionary.
        
        Args:
            tool_names: Names of tools that were executed
            results: Results from tool execution (may include exceptions)
            required_tools: Set of tools that were requested
            collection_time: Time taken for collection (milliseconds)
            
        Returns:
            Context dictionary with results and metadata
        """
        context = {}
        succeeded = []
        failed = []
        failure_details = {}
        
        for tool_name, result in zip(tool_names, results):
            if isinstance(result, Exception):
                failed.append(tool_name)
                failure_details[tool_name] = {
                    "error": str(result),
                    "error_type": type(result).__name__
                }
                logger.error(f"Context collection failed for {tool_name}: {result}")
            elif result is not None:
                context[tool_name] = result
                succeeded.append(tool_name)
            else:
                failed.append(tool_name)
                failure_details[tool_name] = {
                    "error": "Returned None after retries"
                }
        
        # Add metadata
        context["collection_metadata"] = {
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "collection_time_ms": round(collection_time, 2),
            "tools_requested": list(required_tools),
            "tools_succeeded": succeeded,
            "tools_failed": failed,
            "failure_details": failure_details if failure_details else None,
            "parallel_execution": self.parallel_execution
        }
        
        return context
    
    def _create_empty_context(self) -> Dict[str, Any]:
        """Create empty context when no tools are required."""
        return {
            "collection_metadata": {
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "collection_time_ms": 0,
                "tools_requested": [],
                "tools_succeeded": [],
                "tools_failed": [],
                "failure_details": None,
                "parallel_execution": self.parallel_execution
            }
        }
    
    def _create_timeout_context(self, required_tools: Set[str]) -> Dict[str, Any]:
        """Create context when collection times out."""
        return {
            "collection_metadata": {
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "collection_time_ms": self.collection_timeout * 1000,
                "tools_requested": list(required_tools),
                "tools_succeeded": [],
                "tools_failed": list(required_tools),
                "failure_details": {
                    tool: {"error": "Collection timeout", "error_type": "TimeoutError"}
                    for tool in required_tools
                },
                "parallel_execution": self.parallel_execution,
                "timeout": True
            }
        }


# Made with Bob