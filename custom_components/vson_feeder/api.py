"""API client for VSON Fish Feeder."""
from __future__ import annotations

import logging
from typing import Any
import aiohttp

from .const import (
    API_BASE_URL,
    DEFAULT_HEADERS,
    ENDPOINT_QUERY_BLE_HOMEPAGE,
    ENDPOINT_QUERY_BLY_HOMEPAGE,
    ENDPOINT_UPDATE_BLE_FEED,
    ENDPOINT_UPDATE_BLE_PUMP,
    ENDPOINT_UPDATE_BLE_RESET,
    ENDPOINT_UPDATE_BLY_FEED,
    ENDPOINT_UPDATE_BLY_RESET,
)

_LOGGER = logging.getLogger(__name__)


class VsonFeederApiClient:
    """Client for interacting with the VSON Air IoT Cloud API."""

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        """Initialize API client."""
        self._session = session
        self._close_session = False
        self._device_types: dict[str, str] = {}  # mac -> "8615" or "8621"

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
        """Fetch current status of the fish feeder (auto-detecting 8615 vs 8621)."""
        session = await self._get_session()
        formatted_mac = mac.strip().upper()
        data = {"mac": formatted_mac}

        known_type = self._device_types.get(formatted_mac)
        endpoints_to_try: list[tuple[str, str]] = []

        if known_type == "8621":
            endpoints_to_try = [("8621", ENDPOINT_QUERY_BLE_HOMEPAGE), ("8615", ENDPOINT_QUERY_BLY_HOMEPAGE)]
        elif known_type == "8615":
            endpoints_to_try = [("8615", ENDPOINT_QUERY_BLY_HOMEPAGE), ("8621", ENDPOINT_QUERY_BLE_HOMEPAGE)]
        else:
            # Detect by prefix or try 8615 then 8621
            if formatted_mac.startswith("86:21"):
                endpoints_to_try = [("8621", ENDPOINT_QUERY_BLE_HOMEPAGE), ("8615", ENDPOINT_QUERY_BLY_HOMEPAGE)]
            else:
                endpoints_to_try = [("8615", ENDPOINT_QUERY_BLY_HOMEPAGE), ("8621", ENDPOINT_QUERY_BLE_HOMEPAGE)]

        last_err: Exception | None = None
        for dev_type, endpoint in endpoints_to_try:
            url = f"{API_BASE_URL}{endpoint}"
            try:
                async with session.post(
                    url,
                    data=data,
                    headers=DEFAULT_HEADERS,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        res_json = await resp.json(content_type=None)
                        if str(res_json.get("retCode")) == "0":
                            self._device_types[formatted_mac] = dev_type
                            result = res_json.get("result", {})
                            result["_device_type"] = dev_type
                            return result
            except Exception as err:
                last_err = err

        if last_err:
            raise last_err
        raise RuntimeError(f"Could not connect to feeder with MAC {formatted_mac}")

    async def async_feed(self, mac: str, hopper_type: int = 0) -> bool:
        """Trigger manual feeding."""
        session = await self._get_session()
        formatted_mac = mac.strip().upper()

        # Ensure we know the device type
        dev_type = self._device_types.get(formatted_mac)
        if not dev_type:
            try:
                await self.async_get_device_status(formatted_mac)
                dev_type = self._device_types.get(formatted_mac, "8615")
            except Exception:
                dev_type = "8621" if formatted_mac.startswith("86:21") else "8615"

        if dev_type == "8621":
            url = f"{API_BASE_URL}{ENDPOINT_UPDATE_BLE_FEED}"
            data = {"mac": formatted_mac}
        else:
            url = f"{API_BASE_URL}{ENDPOINT_UPDATE_BLY_FEED}"
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
                _LOGGER.info("Feed command succeeded for %s (%s)", formatted_mac, dev_type)
                return True
        except Exception as err:
            _LOGGER.error("Error sending feed command: %s", err)
            return False

    async def async_reset_water_change(self, mac: str) -> bool:
        """Reset water change reminder."""
        session = await self._get_session()
        formatted_mac = mac.strip().upper()

        dev_type = self._device_types.get(formatted_mac)
        if not dev_type:
            try:
                await self.async_get_device_status(formatted_mac)
                dev_type = self._device_types.get(formatted_mac, "8615")
            except Exception:
                dev_type = "8621" if formatted_mac.startswith("86:21") else "8615"

        if dev_type == "8621":
            url = f"{API_BASE_URL}{ENDPOINT_UPDATE_BLE_RESET}"
        else:
            url = f"{API_BASE_URL}{ENDPOINT_UPDATE_BLY_RESET}"

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
                _LOGGER.info("Water change reset succeeded for %s (%s)", formatted_mac, dev_type)
                return True
        except Exception as err:
            _LOGGER.error("Error sending reset water change: %s", err)
            return False

    async def async_set_pump(self, mac: str, is_open: int) -> bool:
        """Control water pump (for WP8621 series)."""
        session = await self._get_session()
        formatted_mac = mac.strip().upper()
        url = f"{API_BASE_URL}{ENDPOINT_UPDATE_BLE_PUMP}"
        data = {"mac": formatted_mac, "isOpen": str(is_open)}

        try:
            async with session.post(url, data=data, headers=DEFAULT_HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to set pump, HTTP %s", resp.status)
                    return False
                res_json = await resp.json(content_type=None)
                if str(res_json.get("retCode")) != "0":
                    _LOGGER.error("Pump command error: %s", res_json)
                    return False
                _LOGGER.info("Set pump (%s) succeeded for %s", is_open, formatted_mac)
                return True
        except Exception as err:
            _LOGGER.error("Error sending set pump command: %s", err)
            return False
