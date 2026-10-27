"""Weather tool — uses the free Open-Meteo API (no API key needed)."""

import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather codes -> short description
WEATHER_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "fog", 51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain", 71: "light snow", 73: "snow",
    75: "heavy snow", 80: "rain showers", 81: "rain showers", 82: "violent rain showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "thunderstorm with hail",
}


def get_weather(city: str, days: int = 3) -> str:
    """
    Get the daily weather forecast for a city.

    Args:
        city: Name of the city, in English (e.g. "Tbilisi", "Kazbegi", "Batumi").
        days: Number of forecast days, from 1 to 7.

    Returns:
        A text forecast with min/max temperature, rain chance and conditions per day,
        or an error message starting with "ERROR".
    """
    days = max(1, min(int(days), 7))
    try:
        geo = requests.get(GEOCODE_URL, params={"name": city, "count": 1}, timeout=10).json()
        if not geo.get("results"):
            return f"ERROR: city '{city}' not found."
        place = geo["results"][0]

        data = requests.get(FORECAST_URL, params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
            "timezone": "auto",
            "forecast_days": days,
        }, timeout=10).json()["daily"]
    except requests.RequestException as e:
        return f"ERROR: weather service unavailable ({e})."

    lines = [f"Forecast for {place['name']}, {place.get('country', '')}:"]
    for i, day in enumerate(data["time"]):
        lines.append(
            f"- {day}: {data['temperature_2m_min'][i]}..{data['temperature_2m_max'][i]} °C, "
            f"rain chance {data['precipitation_probability_max'][i]}%, "
            f"{WEATHER_CODES.get(data['weathercode'][i], 'unknown')}"
        )
    return "\n".join(lines)
