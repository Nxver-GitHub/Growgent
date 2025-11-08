"""
Standard API response wrappers.

Provides consistent response format across all endpoints.
"""

from typing import Any, Optional

from pydantic import BaseModel


class APIResponse(BaseModel):
    """
    Standard API response wrapper.

    All API responses follow this format for consistency.
    """

    status: str = "success"
    data: Any = None
    errors: Optional[list[str]] = None
    message: Optional[str] = None


class APIError(BaseModel):
    """
    Standard API error response.

    Used for error responses.
    """

    status: str = "error"
    error: str
    message: Optional[str] = None
    details: Optional[dict[str, Any]] = None


def success_response(data: Any, message: Optional[str] = None) -> APIResponse:
    """
    Create a success response.

    Args:
        data: Response data
        message: Optional success message

    Returns:
        APIResponse with success status
    """
    return APIResponse(status="success", data=data, message=message)


def error_response(
    error: str, message: Optional[str] = None, details: Optional[dict[str, Any]] = None
) -> APIError:
    """
    Create an error response.

    Args:
        error: Error type or code
        message: Human-readable error message
        details: Optional error details

    Returns:
        APIError response
    """
    return APIError(status="error", error=error, message=message, details=details)

