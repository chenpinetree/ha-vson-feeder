"""API client for VSON Fish Feeder."""
from __future__ import annotations

import logging
from typing import Any
import aiohttp

from .const import (
    API_BASE_URL,
    DEFAULT_HEADERS,
    ENDPOINT_QUERY_HOMEPAGE,
    ENDPOINT_RESET_WATER,
    ENDPOINT_UPDATE_FEED,
)

_LOGGER = logging.getLogger(__name__)


class VsonFeederApiClient:
    """Client for interacting with the VSON Air IoT Cloud API."""

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        """Initialize API client."""
        self._session = session
        self._close_session = False

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create client session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._close_session = True
        return self._session

    async def close(self) -> None:
        """Close session if created internally."""
        if self._close_session and self._session and not self._session.closed:
            await self._session.close()

    async def async_get_device_status(self, mac: str) -> dict[str, Any]:
        """Fetch current status of the fish feeder."""
        session = await self._get_session()
        formatted_mac = mac.strip().upper()
        url = f"{API_BASE_URL}{ENDPOINT_QUERY_HOMEPAGE}"
        data = {"mac": formatted_mac}

        try:
            async with session.post(url, data=data, headers=DEFAULT_HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to query feeder status, HTTP %s", resp.status)
                    raise RuntimeError(f"HTTP error {resp.status}")
                res_json = await resp.json(content_type=None)
                if str(res_json.get("retCode")) != "0":
                    _LOGGER.error("Feeder API error: %s", res_json)
                    raise RuntimeError(f"API error code {res_json.get('retCode')}: {res_json.get('result')}")
                result = res_json.get("result", {})
                return result
        except Exception as err:
            _LOGGER.error("Error communicating with VSON cloud API: %s", err)
            raise

    async def async_feed(self, mac: str, hopper_type: int = 0) -> bool:
        """Trigger manual feeding (hopper_type: 0 for left hopper, 1 for right hopper)."""
        session = await self._get_session()
        formatted_mac = mac.strip().upper()
        url = f"{API_BASE_URL}{ENDPOINT_UPDATE_FEED}"
        data = {"mac": formatted_mac, "type": str(hopper_type)}

        try:
            async with session.post(url, data=data, headers=DEFAULT_HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to trigger feed, HTTP %s", resp.status)
                    return False
                res_json = await resp.json(content_type=None)
                if str(res_json.get("retCode")) != "0":
                    _LOGGER.error("Feed command error: %s", res_json)
                    return False
                _LOGGER.info("Feed command succeeded for %s (hopper: %d)", formatted_mac, hopper_type)
                return True
        except Exception as err:
            _LOGGER.error("Error sending feed command: %s", err)
            return False

    async def async_reset_water_change(self, mac: str) -> bool:
        """Reset water change reminder."""
        session = await self._get_session()
        formatted_mac = mac.strip().upper()
        url = f"{API_BASE_URL}{ENDPOINT_RESET_WATER}"
        data = {"mac": formatted_mac}

        try:
            async with session.post(url, data=data, headers=DEFAULT_HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to reset water change, HTTP %s", resp.status)
                    return False
                res_json = await resp.json(content_type=None)
                if str(res_json.get("retCode")) != "0":
                    _LOGGER.error("Reset water change error: %s", res_json)
                    return False
                _LOGGER.info("Water change reset succeeded for %s", formatted_mac)
                return True
        except Exception as err:
            _LOGGER.error("Error sending reset water change: %s", err)
            return False
