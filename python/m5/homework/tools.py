
from typing import Any, Literal

import httpx
import yfinance as yf
from langchain_core.tools import ToolException, tool

# ---------------------------------------------------
# Helper
# ---------------------------------------------------

def get_json(url: str, params: dict | None = None) -> Any:
    """Send a GET request and return parsed JSON."""
    try:
        response = httpx.get(
            url,
            params=params,
            timeout=10.0,
            follow_redirects=True,
        )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise ToolException(f"API request failed: {exc}") from exc


# ---------------------------------------------------
# Tool 1: Official Joke API
# ---------------------------------------------------

@tool
def get_daily_joke(
    category: Literal["general", "programming", "dad", "knock-knock"] = "general",
) -> dict:
    """Get a random joke from the Official Joke API.

    Use this tool when the user asks for a joke or a funny story.

    Args:
        category: Joke category. Defaults to general.
    """
    if category == "general":
        url = "https://official-joke-api.appspot.com/random_joke"
    else:
        url = (
            "https://official-joke-api.appspot.com"
            f"/jokes/{category}/random"
        )

    data = get_json(url)

    # Category-specific endpoint returns a list.
    if isinstance(data, list):
        if not data:
            raise ToolException("No joke found.")
        data = data[0]

    return {
        "category": data["type"],
        "setup": data["setup"],
        "punchline": data["punchline"],
    }


# ---------------------------------------------------
# Tool 2: Open-Meteo Weather
# ---------------------------------------------------

@tool
def get_weather(
    latitude: float,
    longitude: float,
) -> dict:
    """Get the current weather for a geographic location.

    Use this tool when the user requests current weather,
    temperature, humidity, precipitation, or wind speed.

    Args:
        latitude: Geographic latitude in decimal degrees.
        longitude: Geographic longitude in decimal degrees.
    """
    if not -90 <= latitude <= 90:
        raise ToolException("Latitude must be between -90 and 90.")

    if not -180 <= longitude <= 180:
        raise ToolException("Longitude must be between -180 and 180.")

    data = get_json(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation,"
                "wind_speed_10m,"
                "weather_code"
            ),
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "timezone": "auto",
        },
    )

    current = data["current"]

    return {
        "time": current["time"],
        "temperature_f": current["temperature_2m"],
        "feels_like_f": current["apparent_temperature"],
        "humidity_pct": current["relative_humidity_2m"],
        "precipitation_mm": current["precipitation"],
        "wind_mph": current["wind_speed_10m"],
        "weather_code": current["weather_code"],
    }


# ---------------------------------------------------
# Tool 3: Yahoo Finance
# ---------------------------------------------------

@tool
def get_stock_quote(ticker: str) -> dict:
    """Get the latest available stock or ETF quote from Yahoo Finance.

    Use this tool when the user asks for a stock price,
    ETF price, daily price change, or trading volume.

    Args:
        ticker: Stock symbol, such as AAPL, MSFT, or SPY.
    """
    ticker = ticker.strip().upper()

    if not ticker:
        raise ToolException("Ticker symbol cannot be empty.")

    try:
        stock = yf.Ticker(ticker)
        info = stock.fast_info

        price = info.last_price
        previous_close = info.regular_market_previous_close

        if price is None:
            raise ToolException(f"No quote available for {ticker}.")

        change = (
            price - previous_close
            if previous_close is not None
            else None
        )

        change_pct = (
            100 * change / previous_close
            if previous_close
            else None
        )

        return {
            "ticker": ticker,
            "price": price,
            "previous_close": previous_close,
            "change": change,
            "change_percent": change_pct,
            "currency": info.currency,
            "volume": info.last_volume,
            "market_cap": info.market_cap,
            "exchange": info.exchange,
        }

    except ToolException:
        raise
    except Exception as exc:
        raise ToolException(
            f"Yahoo Finance lookup failed for {ticker}: {exc}"
        ) from exc


