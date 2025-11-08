"""
API routes module.

This module contains all FastAPI route handlers organized by feature.
"""

from app.api import agents, alerts, fields, recommendations, metrics, zones, scheduler, users, farms, user_preferences, satellite, fire_perimeters, psps_events

__all__ = ["agents", "alerts", "fields", "recommendations", "metrics", "zones", "scheduler", "users", "farms", "user_preferences", "satellite", "fire_perimeters", "psps_events"]