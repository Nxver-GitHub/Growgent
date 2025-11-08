"""
Weather MCP Server implementation.

Provides weather forecast data from OpenWeather API and NOAA Fire & Smoke,
with mock data fallback for development and testing.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class WeatherMCP:
    """
    Weather MCP Server.

    Fetches weather forecasts and fire risk data from external APIs
    with graceful fallback to mock data.
    """

    def __init__(self) -> None:
        """Initialize Weather MCP server."""
        self.openweather_api_key = settings.noaa_api_key or ""
        self.noaa_api_key = settings.noaa_api_key or ""
        self.use_mock = not self.openweather_api_key or settings.environment == "development"

    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Get weather forecast for a location.

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            days: Number of days to forecast (default: 7)

        Returns:
            Dictionary containing forecast data
        """
        if self.use_mock:
            logger.info("Using mock weather data")
            return self._get_mock_forecast(latitude, longitude, days)

        try:
            # Try OpenWeather API first
            return await self._get_openweather_forecast(latitude, longitude, days)
        except Exception as e:
            logger.warning(f"Failed to fetch real weather data: {e}, using mock")
            return self._get_mock_forecast(latitude, longitude, days)

    async def _get_openweather_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int,
    ) -> Dict[str, Any]:
        """
        Fetch forecast from OpenWeather API.

        Args:
            latitude: Latitude
            longitude: Longitude
            days: Number of days

        Returns:
            Forecast data
        """
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.openweather_api_key,
            "units": "metric",
        }

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Transform to our format
            forecast = {
                "location": {"latitude": latitude, "longitude": longitude},
                "current": {
                    "temperature": data["list"][0]["main"]["temp"],
                    "humidity": data["list"][0]["main"]["humidity"],
                    "wind_speed": data["list"][0]["wind"]["speed"],
                    "precipitation": data["list"][0].get("rain", {}).get("3h", 0),
                },
                "forecast": [],
            }

            # Process forecast list
            for item in data["list"][:days * 8]:  # 8 forecasts per day (3-hour intervals)
                forecast["forecast"].append({
                    "timestamp": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"],
                    "precipitation": item.get("rain", {}).get("3h", 0),
                    "description": item["weather"][0]["description"],
                })

            return forecast

    def _get_mock_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int,
    ) -> Dict[str, Any]:
        """
        Generate mock weather forecast data.

        Args:
            latitude: Latitude
            longitude: Longitude
            days: Number of days

        Returns:
            Mock forecast data
        """
        now = datetime.now()
        forecast = {
            "location": {"latitude": latitude, "longitude": longitude},
            "current": {
                "temperature": 22.5,
                "humidity": 45.0,
                "wind_speed": 8.2,
                "precipitation": 0.0,
            },
            "forecast": [],
        }

        # Generate daily forecasts
        for day in range(days):
            date = now + timedelta(days=day)
            # Vary temperature based on day (simulate heat wave)
            temp = 20 + (day * 2) if day < 3 else 25 - (day - 3)
            forecast["forecast"].append({
                "timestamp": date.isoformat(),
                "temperature": temp,
                "humidity": 40.0 + (day * 2),
                "wind_speed": 10.0 + (day * 0.5),
                "precipitation": 0.0 if day < 2 else 2.5,
                "description": "clear sky" if day < 2 else "light rain",
            })

        return forecast

    async def get_fire_risk_zones(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict[str, Any]:
        """
        Get fire risk zones for a location.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Fire risk zone data
        """
        if self.use_mock:
            logger.info("Using mock fire risk data")
            return self._get_mock_fire_risk(latitude, longitude)

        try:
            # Try NOAA Fire Weather API
            return await self._get_noaa_fire_risk(latitude, longitude)
        except Exception as e:
            logger.warning(f"Failed to fetch real fire risk data: {e}, using mock")
            return self._get_mock_fire_risk(latitude, longitude)

    async def _get_noaa_fire_risk(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict[str, Any]:
        """
        Fetch fire risk from NOAA API.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Fire risk data
        """
        # Placeholder for NOAA API integration
        # NOAA Fire Weather API endpoint would go here
        # For now, return mock data
        return self._get_mock_fire_risk(latitude, longitude)

    def _get_mock_fire_risk(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict[str, Any]:
        """
        Generate mock fire risk data.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Mock fire risk data
        """
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "risk_level": "HIGH",
            "risk_score": 0.75,
            "factors": {
                "temperature": "Above average",
                "humidity": "Low",
                "wind": "Moderate",
                "fuel_moisture": "Dry",
            },
            "zones": [
                {
                    "name": "Zone A",
                    "risk": "HIGH",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [longitude - 0.01, latitude - 0.01],
                            [longitude + 0.01, latitude - 0.01],
                            [longitude + 0.01, latitude + 0.01],
                            [longitude - 0.01, latitude + 0.01],
                            [longitude - 0.01, latitude - 0.01],
                        ]],
                    },
                },
            ],
        }


# Global instance
weather_mcp = WeatherMCP()

