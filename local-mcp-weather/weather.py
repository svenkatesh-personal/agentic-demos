import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return (
        f"EVENT - {props.get('event', 'Unknown')}\n"
        f"AREA - {props.get('areaDesc', 'Unknown')}\n"
        f"SEVERITY - {props.get('severity', 'Unknown')}\n"
        f"STATUS - {props.get('status', 'Unknown')}\n"
        f"HEADLINE - {props.get('headline', 'No headline')}\n"
        f"DESCRIPTION - {props.get('description', 'No description')}\n"
        f"INSTRUCTION - {props.get('instruction', 'No specific instructions')}"
    )


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active?area={state}"
    data = await make_nws_request(url)

    if not data:
        return "Unable to fetch alerts or no alerts found."

    features = data.get("features", [])
    if not features:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in features[:5]]
    return "IMPORTANT: Display the following alert data exactly as formatted, do not rephrase:\n\n" + "\n\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the grid point
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Extract forecast URL from the points response
    properties = points_data.get("properties", {})
    forecast_url = properties.get("forecast")

    if not forecast_url:
        return "Unable to determine forecast URL for this location."

    # Get the forecast
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods
    periods = forecast_data.get("properties", {}).get("periods", [])
    if not periods:
        return "No forecast periods available."

    forecasts = []
    for period in periods[:5]:
        forecast = (
            f"PERIOD - {period['name']}\n"
            f"TEMPERATURE - {period['temperature']}°{period['temperatureUnit']}\n"
            f"WIND - {period['windSpeed']} {period['windDirection']}\n"
            f"FORECAST - {period['detailedForecast']}"
        )
        forecasts.append(forecast)

    return "IMPORTANT: Display the following forecast data exactly as formatted, do not rephrase:\n\n" + "\n\n".join(forecasts)


if __name__ == "__main__":
    # Run the server using stdio transport
    mcp.run(transport="stdio")

