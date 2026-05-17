"""
News context tool using GDELT DOC 2.0.

Fetches relevant public news/events that might impact shipments:
strikes, natural disasters, customs issues, congestion, port delays, etc.
"""
import httpx
from typing import Dict, Any, List, Optional, Set


async def get_relevant_news(
    location: str, keywords: Optional[List[str]] = None, days_back: int = 7
) -> Dict[str, Any]:
    """
    Get relevant disruption news for a shipment location using GDELT DOC 2.0.

    Args:
        location: Location to search news for.
        keywords: Extra disruption/logistics keywords
        days_back: Number of days to look back.

    Returns:
        Dictionary with:
            - summary
            - articles
            - impact_level
            - categories
            - total_articles
    """
    if keywords is None:
        keywords = [
            "port",
            "shipping",
            "logistics",
            "customs",
            "strike",
            "protest",
            "weather",
            "flood",
            "storm",
            "congestion",
            "delay",
            "backlog",
            "road closure",
            "rail delay",
        ]

    api_url = "https://api.gdeltproject.org/api/v2/doc/doc"

    # GDELT supports timespan strings like "7d", "24h", etc.
    # Keep it bounded so the tool is fast and relevant.
    days_back = max(1, min(days_back, 30))
    timespan = f"{days_back}d"

    # GDELT query syntax is different from NewsAPI.
    # Operators go inside the query string, not as separate URL parameters.
    keyword_query = " OR ".join(
        [f'"{kw}"' if " " in kw else kw for kw in keywords]
    )

    query = f'"{location}" ({keyword_query})'

    params: Dict[str, str | int] = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "timespan": timespan,
        "sort": "HybridRel",
        "maxrecords": 10,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

        # GDELT ArticleList JSON commonly returns an "articles" array.
        raw_articles = data.get("articles", [])

        processed_articles = []
        categories = set()

        for article in raw_articles[:5]:
            title = article.get("title", "") or ""
            description = (
                article.get("seendate", "") or article.get("domain", "") or ""
            )

            category = _categorize_article(title, description)
            categories.add(category)

            processed_articles.append(
                {
                    "title": title,
                    "description": article.get("sourcecountry", ""),
                    "source": article.get("domain", "Unknown"),
                    "published_at": article.get("seendate", ""),
                    "url": article.get("url", ""),
                    "category": category,
                    "language": article.get("language", ""),
                    "source_country": article.get("sourcecountry", ""),
                }
            )

        impact_level = _determine_impact_level(processed_articles, categories)
        summary = _generate_summary(processed_articles, categories)

        return {
            "summary": summary,
            "articles": processed_articles,
            "impact_level": impact_level,
            "categories": list(categories),
            "total_articles": len(raw_articles),
            "provider": "GDELT_DOC_2_0",
            "query": query,
        }

    except httpx.HTTPError as e:
        return {
            "summary": "No recent GDELT news data available",
            "articles": [],
            "impact_level": "none",
            "categories": [],
            "total_articles": 0,
            "provider": "GDELT_DOC_2_0",
            "error": str(e),
        }
    except ValueError as e:
        return {
            "summary": "GDELT returned an unreadable response",
            "articles": [],
            "impact_level": "none",
            "categories": [],
            "total_articles": 0,
            "provider": "GDELT_DOC_2_0",
            "error": str(e),
        }


def _categorize_article(title: str, description: str) -> str:
    content = f"{title} {description}".lower()

    if any(
        word in content
        for word in ["strike", "protest", "walkout", "labor", "union"]
    ):
        return "labor_action"
    elif any(
        word in content
        for word in [
            "storm",
            "hurricane",
            "typhoon",
            "flood",
            "earthquake",
            "wildfire",
        ]
    ):
        return "natural_disaster"
    elif any(
        word in content
        for word in ["customs", "tariff", "regulation", "policy", "inspection"]
    ):
        return "regulatory"
    elif any(
        word in content
        for word in ["congestion", "delay", "backlog", "queue", "bottleneck"]
    ):
        return "operational"
    elif any(
        word in content
        for word in [
            "security",
            "threat",
            "cyberattack",
            "closure",
            "evacuation",
        ]
    ):
        return "security"
    elif any(
        word in content
        for word in ["port", "terminal", "vessel", "container", "shipping"]
    ):
        return "port_logistics"
    else:
        return "general"


def _determine_impact_level(
    articles: List[Dict[str, Any]],
    categories: Set[str],
) -> str:
    """Determine likely shipment impact from article categories."""
    if not articles or not categories:
        return "none"

    high_impact_categories = {
        "labor_action",
        "natural_disaster",
        "security",
    }
    medium_impact_categories = {
        "operational",
        "regulatory",
        "port_logistics",
    }

    if categories & high_impact_categories:
        return "high"
    if categories & medium_impact_categories:
        return "medium"
    return "low"


def _generate_summary(
    articles: List[Dict[str, Any]],
    categories: Set[str],
) -> str:
    """Generate a short summary for the news context response."""
    if not articles:
        return "No recent disruption news found"

    category_labels = {
        "labor_action": "labor action",
        "natural_disaster": "weather or natural disaster",
        "regulatory": "regulatory issues",
        "operational": "operational delays",
        "security": "security issues",
        "port_logistics": "port logistics updates",
        "general": "general updates",
    }

    issues = [
        category_labels.get(category, category)
        for category in categories
        if category != "general"
    ]

    if not issues:
        return f"Found {len(articles)} recent general news articles"
    if len(issues) == 1:
        return f"Found recent news related to {issues[0]}"
    return f"Found recent news across multiple issues: {', '.join(issues)}"


# Made with Bob
