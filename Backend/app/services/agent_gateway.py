"""
Agent Gateway for IBM Watsonx AI-powered alert analysis.

Connects to IBM Watsonx Orchestrate API for real-time freight exception analysis.
"""
import httpx
from decimal import Decimal
from typing import Dict, Any

from app.config import settings
from app.models.alert import Alert
from app.models.shipment import Shipment


class AgentGateway:
    """
    Gateway for communicating with IBM Watsonx AI agent.

    Handles authentication, request formatting, and response parsing
    for the Freight Exception Analyst agent deployed in Watsonx.
    """

    def __init__(self, agent_version: str = "1.0.0"):
        """
        Initialize agent gateway.

        Args:
            agent_version: Version identifier for the agent
        """
        self.agent_version = agent_version
        self.watsonx_url = settings.watsonx_api_url
        self.api_key = settings.watsonx_api_key
        self.timeout = settings.agent_timeout_seconds

    async def analyze_alert(
        self, alert: Alert, shipment: Shipment, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze an alert using IBM Watsonx AI agent with pre-collected context.

        The agent receives all context data upfront and performs analysis
        without needing to call external tools.

        Args:
            alert: Alert to analyze
            shipment: Associated shipment
            context: Pre-collected context data from ContextService

        Returns:
            Analysis result dictionary with:
                - likely_cause: str
                - risk_priority: str
                - confidence_level: Decimal
                - supporting_evidence: dict
                - external_factors: dict

        Raises:
            httpx.HTTPError: If Watsonx API call fails
            ValueError: If response parsing fails
        """
        # Prepare request payload for Watsonx with context
        payload = self._prepare_watsonx_payload(alert, shipment, context)

        # Set up authentication headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            # Add any additional Watsonx-specific headers here
            # "X-Watson-Project-ID": "your-project-id",
            # "X-Watson-Agent-ID": "freight-exception-analyst",
        }

        # Call Watsonx API
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.watsonx_url}/analyze",  # TODO: Replace with actual Watsonx endpoint
                json=payload,
                headers=headers,
            )
            response.raise_for_status()

            # Parse Watsonx response
            watsonx_result = response.json()

            # Transform Watsonx response to our format
            analysis = self._parse_watsonx_response(watsonx_result)

            return analysis

    def _prepare_watsonx_payload(
        self, alert: Alert, shipment: Shipment, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare payload for Watsonx API request with pre-collected context.

        Formats alert, shipment, and context data into the structure
        expected by the Watsonx Freight Exception Analyst agent.
        The agent receives all context upfront for analysis.

        Args:
            alert: Alert to analyze
            shipment: Associated shipment
            context: Pre-collected context data from ContextService

        Returns:
            Formatted payload dictionary
        """
        return {
            # TODO: Customize based on your Watsonx agent's expected input format
            "agent_id": "freight-exception-analyst",  # Replace with your agent ID
            "input": {
                "alert": {
                    "id": str(alert.id),
                    "type": alert.alert_type,
                    "priority": alert.priority,
                    "status": alert.status,
                    "detected_at": alert.detected_at.isoformat(),
                    "backend_reason": alert.backend_reason,
                    "milestone_type": alert.milestone_type,
                    "expected_time": alert.expected_time.isoformat()
                    if alert.expected_time
                    else None,
                    "actual_time": alert.actual_time.isoformat()
                    if alert.actual_time
                    else None,
                    "delay_minutes": alert.delay_minutes,
                },
                "shipment": {
                    "id": str(shipment.id),
                    "tracking_number": shipment.tracking_number,
                    "origin": shipment.origin,
                    "destination": shipment.destination,
                    "current_status": shipment.current_status,
                    "current_location": shipment.current_location,
                    "customer_id": shipment.customer_id,
                },
                "context": context,  # NEW: Pre-collected context data
            },
            "parameters": {
                "max_tokens": 500,
                "temperature": 0.7,
                "return_structured_output": True,
            },
        }

    def _parse_watsonx_response(
        self, watsonx_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse Watsonx API response into our analysis format.

        Extracts the relevant fields from Watsonx response and converts
        them to the format expected by our AlertAnalysis model.

        Args:
            watsonx_result: Raw response from Watsonx API

        Returns:
            Parsed analysis dictionary

        Raises:
            ValueError: If required fields are missing from response
        """
        # TODO: Customize based on your Watsonx agent's output format
        # This is a generic example - adjust field names and structure as needed

        output = watsonx_result.get("output", {})

        # Validate required fields
        if not output.get("likely_cause"):
            raise ValueError("Watsonx response missing 'likely_cause' field")

        # Extract and convert confidence level to Decimal
        confidence_raw = output.get("confidence_level", 0.75)
        if isinstance(confidence_raw, str):
            confidence = Decimal(confidence_raw)
        else:
            confidence = Decimal(str(confidence_raw))

        return {
            "likely_cause": output.get("likely_cause"),
            "risk_priority": output.get("risk_priority", "MEDIUM"),
            "confidence_level": confidence,
            "supporting_evidence": output.get("supporting_evidence", {}),
            "external_factors": output.get("external_factors", {}),
        }


# Made with Bob
