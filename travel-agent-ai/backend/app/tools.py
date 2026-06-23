"""
Tools for the Travel Agent.

These are plain LangChain @tool functions today. Later, when you add MCP,
you'll register an MCP client and these same function signatures can be
swapped for MCP tool calls with almost no change to agent.py.
"""
import os
import requests
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get current weather for a city. Use this when the user asks about
    weather, climate, or 'best time to visit' for a destination."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return f"(Demo mode) Weather data for {city}: Mild, 22°C, partly cloudy."
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        r = requests.get(url, timeout=5)
        data = r.json()
        if r.status_code != 200:
            return f"Could not fetch weather for {city}: {data.get('message', 'unknown error')}"
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"Weather in {city}: {temp}°C, {desc}."
    except Exception as e:
        return f"Weather lookup failed: {e}"


@tool
def estimate_budget(destination: str, days: int, travel_style: str = "mid-range") -> str:
    """Estimate a rough total trip budget in USD for a destination, number
    of days, and travel style (budget / mid-range / luxury)."""
    daily_rates = {"budget": 60, "mid-range": 150, "luxury": 400}
    rate = daily_rates.get(travel_style.lower(), 150)
    total = rate * days
    return (
        f"Estimated budget for {days} days in {destination} ({travel_style}): "
        f"~${total} USD total (~${rate}/day, covers lodging, food, local transport; "
        f"excludes international flights)."
    )


@tool
def search_attractions(destination: str) -> str:
    """Look up well-known attractions and activities for a destination.
    Use this to ground itinerary suggestions in real points of interest."""
    # Placeholder static logic — swap for Tavily/SerpAPI/Google Places later.
    return (
        f"Top attractions in {destination} typically include: historic old town/center, "
        f"a major museum or cultural landmark, a local food market, and at least one "
        f"nature or scenic viewpoint nearby. (Swap this tool for a live search API for "
        f"real-time, destination-specific results.)"
    )


ALL_TOOLS = [get_weather, estimate_budget, search_attractions]
