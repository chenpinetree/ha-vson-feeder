"""Sensor platform for VSON Fish Feeder."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import VsonFeederCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VSON Fish Feeder sensors based on a config entry."""
    coordinator: VsonFeederCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        VsonFeederBatterySensor(coordinator),
        VsonFeederWaterCleanlinessSensor(coordinator),
        VsonFeederLastWaterChangeSensor(coordinator),
        VsonFeederLastFeedLeftSensor(coordinator),
        VsonFeederLastFeedRightSensor(coordinator),
        VsonFeederPeriodSensor(coordinator),
    ]

    async_add_entities(entities)


class VsonFeederBaseEntity(CoordinatorEntity[VsonFeederCoordinator]):
    """Base entity for VSON Fish Feeder."""

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


class VsonFeederBatterySensor(VsonFeederBaseEntity, SensorEntity):
    """Battery level percentage sensor."""

    _attr_translation_key = "battery"
    _attr_name = "电量"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize battery sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_battery"

    @property
    def native_value(self) -> int | None:
        """Return the battery percentage."""
        return self.coordinator.data.get("battery_percent")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "battery_bars": self.coordinator.data.get("battery_bars"),
        }


class VsonFeederWaterCleanlinessSensor(VsonFeederBaseEntity, SensorEntity):
    """Water cleanliness / filter reminder sensor."""

    _attr_translation_key = "water_cleanliness"
    _attr_name = "水质洁净度"
    _attr_icon = "mdi:water-percent"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize water cleanliness sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_water_cleanliness"

    @property
    def native_value(self) -> float | None:
        """Return water cleanliness percentage."""
        return self.coordinator.data.get("water_cleanliness")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        return {
            "period_days": self.coordinator.data.get("period_days"),
            "elapsed_days": self.coordinator.data.get("elapsed_water_change_days"),
        }


class VsonFeederLastWaterChangeSensor(VsonFeederBaseEntity, SensorEntity):
    """Last water change timestamp sensor."""

    _attr_translation_key = "last_water_change"
    _attr_name = "上次换水时间"
    _attr_icon = "mdi:water-check"

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize last water change sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_last_water_change"

    @property
    def native_value(self) -> str | None:
        """Return the timestamp string."""
        return self.coordinator.data.get("change_water_time")


class VsonFeederLastFeedLeftSensor(VsonFeederBaseEntity, SensorEntity):
    """Left hopper last feeding time."""

    _attr_translation_key = "last_feed_left"
    _attr_name = "左仓上次投喂时间"
    _attr_icon = "mdi:clock-check-outline"

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize left feed sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_last_feed_left"

    @property
    def native_value(self) -> str | None:
        """Return the last left feeding timestamp."""
        return self.coordinator.data.get("last_feed_time_left") or "暂无记录"


class VsonFeederLastFeedRightSensor(VsonFeederBaseEntity, SensorEntity):
    """Right hopper last feeding time."""

    _attr_translation_key = "last_feed_right"
    _attr_name = "右仓上次投喂时间"
    _attr_icon = "mdi:clock-check-outline"

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize right feed sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_last_feed_right"

    @property
    def native_value(self) -> str | None:
        """Return the last right feeding timestamp."""
        return self.coordinator.data.get("last_feed_time_right") or "暂无记录"


class VsonFeederPeriodSensor(VsonFeederBaseEntity, SensorEntity):
    """Water change cycle period in days."""

    _attr_translation_key = "water_change_period"
    _attr_name = "换水周期"
    _attr_icon = "mdi:calendar-sync"
    _attr_native_unit_of_measurement = "d"

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize period sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_period"

    @property
    def native_value(self) -> int | None:
        """Return cycle in days."""
        return self.coordinator.data.get("period_days")
