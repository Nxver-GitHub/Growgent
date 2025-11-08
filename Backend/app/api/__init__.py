"""
API routes module.

This module contains all FastAPI route handlers organized by feature.
"""

from app.api import agents, alerts, fields, recommendations, metrics

__all__ = ["agents", "alerts", "fields", "recommendations", "metrics"]