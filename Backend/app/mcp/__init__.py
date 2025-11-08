"""
MCP servers module.

This module contains Model Context Protocol server implementations.
"""

from app.mcp.client import MCPClient, MCPClientError, MCPTimeoutError
from app.mcp.weather import WeatherMCP, weather_mcp
from app.mcp.psps import PSPSMCP
from app.mcp.sensor import SensorMCP, sensor_mcp
from app.mcp.fire_risk import FireRiskMCP, fire_risk_mcp

# Create global instances for PSPSMCP (not created in module)
psps_mcp = PSPSMCP()

__all__ = [
    "MCPClient",
    "MCPClientError",
    "MCPTimeoutError",
    "WeatherMCP",
    "weather_mcp",
    "PSPSMCP",
    "psps_mcp",
    "SensorMCP",
    "sensor_mcp",
    "FireRiskMCP",
    "fire_risk_mcp",
]