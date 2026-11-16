"""Config flow for VSON Fish Feeder integration."""
from __future__ import annotations

import logging
import re
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import VsonFeederApiClient
from .const import CONF_MAC, DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

MAC_REGEX = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")


class VsonFeederConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for VSON Fish Feeder."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            raw_mac = user_input[CONF_MAC].strip()
            # Normalize MAC to standard XX:XX:XX:XX:XX:XX uppercase
            clean_mac = raw_mac.replace("-", ":").upper()

            if not MAC_REGEX.match(clean_mac):
                errors[CONF_MAC] = "invalid_mac"
            else:
                session = async_get_clientsession(self.hass)
                api = VsonFeederApiClient(session)
                try:
                    status = await api.async_get_device_status(clean_mac)
                    if not status:
                        errors["base"] = "cannot_connect"
                except Exception as err:
                    _LOGGER.error("Failed to connect to feeder with MAC %s: %s", clean_mac, err)
                    errors["base"] = "cannot_connect"

                if not errors:
                    await self.async_set_unique_id(clean_mac)
                    self._abort_if_unique_id_configured()

                    title = user_input.get(CONF_NAME) or f"{DEFAULT_NAME} ({clean_mac[-5:]})"
                    return self.async_create_entry(
                        title=title,
                        data={
                            CONF_MAC: clean_mac,
                        },
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_MAC, default="86:15:02:FB:BB:A3"): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
