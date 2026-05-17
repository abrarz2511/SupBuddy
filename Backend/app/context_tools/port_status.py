"""
Port status context tool.

Fetches port-specific news and events using news API to provide
context about port operations, congestion, strikes, weather impacts, etc.
"""
import httpx
from typing import Dict, Any, List, Set


async def get_port_status(
    port_name: str, days_back: int = 7
) -> Dict[str, Any]:
    """
    Get port status by searching for relevant news about the port.

    Uses news API to find articles about port operations, delays,
    strikes, weather impacts, congestion, and other relevant events.

    Args:
        port_name: Name of the port.
        days_back: Number of days to look back for news (default: 7)

    Returns:
        Dictionary with port information derived from news:
            - summary: str (brief summary of port status)
            - operational_status: str (inferred from news)
            - congestion_level: str (inferred from news)
            - articles: list of relevant news articles
            - impact_level: str ("none", "low", "medium", "high")
            - categories: list of issue categories found
            - total_articles: int
    """
    # Port-specific keywords to search for
    port_keywords = [
        "congestion",
        "delay",
        "backlog",
        "strike",
        "protest",
        "closure",
        "weather",
        "storm",
        "customs",
        "inspection",
        "capacity",
        "operations",
        "disruption",
        "vessel queue",
        "berth availability",
    ]

    # Use GDELT DOC 2.0 API (free, no API key required)
    api_url = "https://api.gdeltproject.org/api/v2/doc/doc"

    # Limit days_back to reasonable range
    days_back = max(1, min(days_back, 30))
    timespan = f"{days_back}d"

    # Build query for port-specific news
    keyword_query = " OR ".join(
        [f'"{kw}"' if " " in kw else kw for kw in port_keywords]
    )
    query = f'"{port_name}" ({keyword_query})'

    params: Dict[str, str | int] = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "timespan": timespan,
        "sort": "HybridRel",  # Hybrid relevance sorting
        "maxrecords": 15,  # Get more articles for better analysis
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

        # Parse GDELT response
        articles = data.get("articles", [])

        # Process articles to extract port status information
        processed_articles = []
        categories = set()

        for article in articles[:10]:  # Limit to top 10 most relevant
            title = article.get("title", "")
            url = article.get("url", "")
            seendate = article.get("seendate", "")

            # Categorize the article
            category = _categorize_port_article(title)
            if category:
                categories.add(category)

            processed_articles.append(
                {
                    "title": title,
                    "url": url,
                    "date": seendate,
                    "category": category,
                    "source": article.get("domain", "Unknown"),
                }
            )

        # Infer port status from articles
        operational_status = _infer_operational_status(
            processed_articles, categories
        )
        congestion_level = _infer_congestion_level(
            processed_articles, categories
        )
        impact_level = _determine_port_impact_level(categories)

        # Generate summary
        summary = _generate_port_summary(port_name, categories, len(articles))

        return {
            "summary": summary,
            "operational_status": operational_status,
            "congestion_level": congestion_level,
            "articles": processed_articles,
            "impact_level": impact_level,
            "categories": list(categories),
            "total_articles": len(articles),
            "port_name": port_name,
            "search_period_days": days_back,
        }

    except httpx.HTTPError as e:
        # Return fallback data if API fails
        return {
            "summary": f"Unable to retrieve current status for {port_name}",
            "operational_status": "unknown",
            "congestion_level": "unknown",
            "articles": [],
            "impact_level": "none",
            "categories": [],
            "total_articles": 0,
            "port_name": port_name,
            "error": str(e),
        }


def _categorize_port_article(title: str) -> str:
    """
    Categorize a port-related news article.

    Args:
        title: Article title

    Returns:
        Category string
    """
    title_lower = title.lower()

    # Check for different types of port issues
    if any(
        word in title_lower
        for word in ["strike", "walkout", "protest", "labor"]
    ):
        return "labor_action"
    elif any(
        word in title_lower
        for word in ["storm", "hurricane", "typhoon", "flood", "weather"]
    ):
        return "weather_impact"
    elif any(
        word in title_lower
        for word in ["congestion", "backlog", "queue", "delay"]
    ):
        return "congestion"
    elif any(
        word in title_lower
        for word in ["closure", "closed", "shutdown", "suspended"]
    ):
        return "closure"
    elif any(
        word in title_lower for word in ["customs", "inspection", "security"]
    ):
        return "customs_security"
    elif any(
        word in title_lower for word in ["capacity", "expansion", "upgrade"]
    ):
        return "capacity_change"
    else:
        return "general"


def _infer_operational_status(
    articles: List[Dict[str, Any]],
    categories: Set[str],
) -> str:
    """
    Infer operational status from news articles.

    Args:
        articles: List of processed articles
        categories: Set of categories found

    Returns:
        Operational status: "operational", "limited", "closed", or "unknown"
    """
    if "closure" in categories:
        return "closed"
    elif "labor_action" in categories or "weather_impact" in categories:
        return "limited"
    elif "congestion" in categories:
        return "operational"  # Operating but congested
    elif articles:
        return "operational"
    else:
        return "unknown"


def _infer_congestion_level(
    articles: List[Dict[str, Any]],
    categories: Set[str],
) -> str:
    """
    Infer congestion level from news articles.

    Args:
        articles: List of processed articles
        categories: Set of categories found

    Returns:
        Congestion level: "low", "medium", "high", "critical", or "unknown"
    """
    if "closure" in categories or "labor_action" in categories:
        return "critical"
    elif "congestion" in categories:
        # Count congestion-related articles
        congestion_count = sum(
            1 for a in articles if a.get("category") == "congestion"
        )
        if congestion_count >= 3:
            return "high"
        elif congestion_count >= 1:
            return "medium"
        else:
            return "low"
    elif "weather_impact" in categories:
        return "medium"
    elif articles:
        return "low"
    else:
        return "unknown"


def _determine_port_impact_level(categories: Set[str]) -> str:
    """
    Determine overall impact level based on news categories.

    Args:
        categories: Set of categories found

    Returns:
        Impact level: "none", "low", "medium", or "high"
    """
    if not categories:
        return "none"

    # High impact categories
    if "closure" in categories or "labor_action" in categories:
        return "high"

    # Medium impact categories
    if (
        "weather_impact" in categories
        or "congestion" in categories
        or "customs_security" in categories
    ):
        return "medium"

    # Low impact for other issues
    if categories:
        return "low"

    return "none"


def _generate_port_summary(
    port_name: str,
    categories: Set[str],
    article_count: int,
) -> str:
    """
    Generate a brief summary of port status.

    Args:
        port_name: Name of the port
        categories: Set of categories found
        article_count: Number of articles found

    Returns:
        Summary string
    """
    if article_count == 0:
        return f"No recent news or disruptions reported for {port_name}"

    category_descriptions = {
        "labor_action": "labor strikes or protests",
        "weather_impact": "severe weather impacts",
        "congestion": "congestion and delays",
        "closure": "operational closures",
        "customs_security": "customs or security issues",
        "capacity_change": "capacity changes",
        "general": "operational updates",
    }

    issues = [
        category_descriptions.get(cat, cat)
        for cat in categories
        if cat != "general"
    ]
    # Filter out None values
    issues = [issue for issue in issues if issue is not None]

    if not issues:
        return (
            f"{port_name} has recent operational updates "
            f"({article_count} articles)"
        )
    elif len(issues) == 1:
        return f"{port_name} experiencing {issues[0]}"
    elif len(issues) == 2:
        return f"{port_name} experiencing {issues[0]} and {issues[1]}"
    else:
        issue_list = ", ".join(issues[:-1])
        return (
            f"{port_name} experiencing multiple issues: "
            f"{issue_list}, and {issues[-1]}"
        )


# Made with Bob
