"""Switch platform for VSON Fish Feeder."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import VsonFeederCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VSON Fish Feeder switch entities."""
    coordinator: VsonFeederCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SwitchEntity] = []

    if coordinator.data.get("has_pump"):
        entities.append(VsonFeederPumpSwitch(coordinator))

    if entities:
        async_add_entities(entities)


class VsonFeederBaseSwitch(CoordinatorEntity[VsonFeederCoordinator], SwitchEntity):
    """Base switch for VSON Feeder."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize base switch."""
        super().__init__(coordinator)
        self._mac = coordinator.mac
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._mac)},
            name=f"{coordinator.data.get('model', '智能喂鱼器')} ({self._mac[-5:]})",
            manufacturer="VSON (威盛)",
            model=coordinator.data.get("model", "WP8615"),
            sw_version=coordinator.data.get("version"),
        )


class VsonFeederPumpSwitch(VsonFeederBaseSwitch):
    """Water pump switch for models with pump support."""

    _attr_translation_key = "pump"
    _attr_name = "水泵"
    _attr_icon = "mdi:water-pump"

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize pump switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_pump"

    @property
    def is_on(self) -> bool:
        """Return True if pump is on."""
        return bool(self.coordinator.data.get("is_pump"))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the pump."""
        _LOGGER.info("Turning on water pump for %s", self._mac)
        success = await self.coordinator.api.async_set_pump(self._mac, 1)
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the pump."""
        _LOGGER.info("Turning off water pump for %s", self._mac)
        success = await self.coordinator.api.async_set_pump(self._mac, 0)
        if success:
            await self.coordinator.async_request_refresh()
