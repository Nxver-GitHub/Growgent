"""
MCP Client wrapper for JSON-RPC 2.0 communication.

This module provides a client for communicating with MCP servers
using the JSON-RPC 2.0 protocol with error handling, timeouts, and retries.
"""

import json
import logging
from typing import Any, Dict, Optional
from uuid import uuid4

import httpx

logger = logging.getLogger(__name__)


class MCPClientError(Exception):
    """Base exception for MCP client errors."""

    pass


class MCPTimeoutError(MCPClientError):
    """Exception raised when MCP request times out."""

    pass


class MCPClient:
    """
    MCP Client for JSON-RPC 2.0 communication.

    Handles communication with MCP servers, including error handling,
    timeouts, and automatic retries.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        max_retries: int = 2,
    ) -> None:
        """
        Initialize MCP client.

        Args:
            base_url: Base URL of the MCP server
            timeout: Request timeout in seconds (default: 5.0)
            max_retries: Maximum number of retry attempts (default: 2)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)

    async def call(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Call an MCP server method using JSON-RPC 2.0.

        Args:
            method: Method name to call
            params: Optional parameters for the method

        Returns:
            Response data from the MCP server

        Raises:
            MCPTimeoutError: If request times out
            MCPClientError: If request fails after retries
        """
        request_id = str(uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }

        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(
                    f"MCP call: {method} (attempt {attempt + 1}/{self.max_retries + 1})"
                )

                response = await self.client.post(
                    self.base_url,
                    json=payload,
                )
                response.raise_for_status()

                data = response.json()

                # Check for JSON-RPC error
                if "error" in data:
                    error = data["error"]
                    logger.error(
                        f"MCP error: {error.get('code')} - {error.get('message')}"
                    )
                    raise MCPClientError(
                        f"MCP server error: {error.get('message', 'Unknown error')}"
                    )

                # Return result
                if "result" in data:
                    return data["result"]

                raise MCPClientError("Invalid JSON-RPC response: missing result")

            except httpx.TimeoutException as e:
                last_error = MCPTimeoutError(f"Request to {self.base_url} timed out")
                logger.warning(f"MCP timeout (attempt {attempt + 1}): {last_error}")
                if attempt < self.max_retries:
                    continue
                raise last_error

            except httpx.HTTPStatusError as e:
                last_error = MCPClientError(
                    f"HTTP error {e.response.status_code}: {e.response.text}"
                )
                logger.error(f"MCP HTTP error: {last_error}")
                if attempt < self.max_retries:
                    continue
                raise last_error

            except Exception as e:
                last_error = MCPClientError(f"Unexpected error: {str(e)}")
                logger.error(f"MCP unexpected error: {last_error}")
                if attempt < self.max_retries:
                    continue
                raise last_error

        # Should never reach here, but just in case
        if last_error:
            raise last_error
        raise MCPClientError("Unknown error occurred")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "MCPClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

