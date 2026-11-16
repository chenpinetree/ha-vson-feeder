"""Button platform for VSON Fish Feeder."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
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
    """Set up VSON Fish Feeder buttons."""
    coordinator: VsonFeederCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        VsonFeederFeedLeftButton(coordinator),
        VsonFeederFeedRightButton(coordinator),
        VsonFeederResetWaterButton(coordinator),
    ]

    async_add_entities(entities)


class VsonFeederBaseButton(CoordinatorEntity[VsonFeederCoordinator], ButtonEntity):
    """Base button for VSON Feeder."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._mac = coordinator.mac
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._mac)},
            name=f"智能喂鱼器 ({self._mac[-5:]})",
            manufacturer="VSON (威盛)",
            model="WP8615",
            sw_version=coordinator.data.get("version", "WP8615_S05"),
        )


class VsonFeederFeedLeftButton(VsonFeederBaseButton):
    """Button to trigger manual left hopper feed."""

    _attr_translation_key = "feed_left"
    _attr_name = "立即投喂 (左仓)"
    _attr_icon = "mdi:fishbowl"

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_feed_left"

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Feeding left hopper for feeder %s", self._mac)
        success = await self.coordinator.api.async_feed(self._mac, 0)
        if success:
            await self.coordinator.async_request_refresh()


class VsonFeederFeedRightButton(VsonFeederBaseButton):
    """Button to trigger manual right hopper feed."""

    _attr_translation_key = "feed_right"
    _attr_name = "立即投喂 (右仓)"
    _attr_icon = "mdi:fishbowl-outline"

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_feed_right"

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Feeding right hopper for feeder %s", self._mac)
        success = await self.coordinator.api.async_feed(self._mac, 1)
        if success:
            await self.coordinator.async_request_refresh()


class VsonFeederResetWaterButton(VsonFeederBaseButton):
    """Button to reset water change reminder timer."""

    _attr_translation_key = "reset_water_change"
    _attr_name = "重置换水计时"
    _attr_icon = "mdi:water-sync"

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_reset_water_change"

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Resetting water change timer for feeder %s", self._mac)
        success = await self.coordinator.api.async_reset_water_change(self._mac)
        if success:
            await self.coordinator.async_request_refresh()
