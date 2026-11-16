"""The VSON Fish Feeder integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .api import VsonFeederApiClient
from .const import CONF_MAC, DOMAIN
from .coordinator import VsonFeederCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SWITCH,
]

SERVICE_FEED = "feed"
SERVICE_RESET_WATER = "reset_water_change"
SERVICE_SET_PUMP = "set_pump"

FEED_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MAC): cv.string,
        vol.Optional("hopper", default="left"): vol.In(["left", "right", "0", "1"]),
    }
)

RESET_WATER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MAC): cv.string,
    }
)

SET_PUMP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MAC): cv.string,
        vol.Required("state"): cv.boolean,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up VSON Fish Feeder from a config entry."""
    mac = entry.data[CONF_MAC].strip().upper()
    session = async_get_clientsession(hass)
    api = VsonFeederApiClient(session)

    coordinator = VsonFeederCoordinator(hass, api, mac)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register custom domain services if not already registered
    if not hass.services.has_service(DOMAIN, SERVICE_FEED):
        async def handle_feed(call: ServiceCall) -> None:
            """Handle manual feed service call."""
            target_mac = call.data[CONF_MAC].strip().upper()
            hopper_raw = str(call.data.get("hopper", "left")).lower()
            hopper_type = 1 if hopper_raw in ("right", "1") else 0

            coord: VsonFeederCoordinator | None = None
            for c in hass.data.get(DOMAIN, {}).values():
                if isinstance(c, VsonFeederCoordinator) and c.mac == target_mac:
                    coord = c
                    break

            if coord:
                success = await coord.api.async_feed(target_mac, hopper_type)
                if success:
                    await coord.async_request_refresh()
            else:
                _LOGGER.warning("Coordinator not found for MAC %s to feed", target_mac)

        async def handle_reset_water(call: ServiceCall) -> None:
            """Handle reset water change service call."""
            target_mac = call.data[CONF_MAC].strip().upper()
            coord: VsonFeederCoordinator | None = None
            for c in hass.data.get(DOMAIN, {}).values():
                if isinstance(c, VsonFeederCoordinator) and c.mac == target_mac:
                    coord = c
                    break

            if coord:
                success = await coord.api.async_reset_water_change(target_mac)
                if success:
                    await coord.async_request_refresh()
            else:
                _LOGGER.warning("Coordinator not found for MAC %s to reset water change", target_mac)

        async def handle_set_pump(call: ServiceCall) -> None:
            """Handle pump control service call."""
            target_mac = call.data[CONF_MAC].strip().upper()
            state = 1 if call.data.get("state") else 0
            coord: VsonFeederCoordinator | None = None
            for c in hass.data.get(DOMAIN, {}).values():
                if isinstance(c, VsonFeederCoordinator) and c.mac == target_mac:
                    coord = c
                    break

            if coord:
                success = await coord.api.async_set_pump(target_mac, state)
                if success:
                    await coord.async_request_refresh()
            else:
                _LOGGER.warning("Coordinator not found for MAC %s to set pump", target_mac)

        hass.services.async_register(DOMAIN, SERVICE_FEED, handle_feed, schema=FEED_SERVICE_SCHEMA)
        hass.services.async_register(DOMAIN, SERVICE_RESET_WATER, handle_reset_water, schema=RESET_WATER_SCHEMA)
        hass.services.async_register(DOMAIN, SERVICE_SET_PUMP, handle_set_pump, schema=SET_PUMP_SCHEMA)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
