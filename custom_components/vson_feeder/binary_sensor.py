"""Binary sensor platform for VSON Fish Feeder."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
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
    """Set up VSON Fish Feeder binary sensors."""
    coordinator: VsonFeederCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[BinarySensorEntity] = [
        VsonFeederConnectivityBinarySensor(coordinator),
        VsonFeederFoodShortageBinarySensor(coordinator),
        VsonFeederWaterChangeDueBinarySensor(coordinator),
    ]

    # Charging and external power sensors (if reported by device)
    if coordinator.data.get("is_charging") is not None:
        entities.append(VsonFeederChargingBinarySensor(coordinator))
    if coordinator.data.get("power_plugged") is not None:
        entities.append(VsonFeederPowerBinarySensor(coordinator))

    async_add_entities(entities)


class VsonFeederBaseBinarySensor(CoordinatorEntity[VsonFeederCoordinator], BinarySensorEntity):
    """Base binary sensor for VSON Feeder."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._mac = coordinator.mac
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._mac)},
            name=f"{coordinator.data.get('model', '智能喂鱼器')} ({self._mac[-5:]})",
            manufacturer="VSON (威盛)",
            model=coordinator.data.get("model", "WP8615"),
            sw_version=coordinator.data.get("version"),
        )


class VsonFeederConnectivityBinarySensor(VsonFeederBaseBinarySensor):
    """Feeder online/connectivity binary sensor."""

    _attr_translation_key = "connectivity"
    _attr_name = "在线状态"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize connectivity sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_connectivity"

    @property
    def is_on(self) -> bool:
        """Return True if device is online."""
        return bool(self.coordinator.data.get("is_online"))


class VsonFeederChargingBinarySensor(VsonFeederBaseBinarySensor):
    """Feeder battery charging binary sensor."""

    _attr_translation_key = "is_charging"
    _attr_name = "充电状态"
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize charging sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_is_charging"

    @property
    def is_on(self) -> bool:
        """Return True if charging."""
        return bool(self.coordinator.data.get("is_charging"))


class VsonFeederPowerBinarySensor(VsonFeederBaseBinarySensor):
    """Feeder external power connected binary sensor."""

    _attr_translation_key = "power_plugged"
    _attr_name = "外部电源连接"
    _attr_device_class = BinarySensorDeviceClass.PLUG

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize power sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_power_plugged"

    @property
    def is_on(self) -> bool:
        """Return True if plugged into external power."""
        return bool(self.coordinator.data.get("power_plugged"))


class VsonFeederFoodShortageBinarySensor(VsonFeederBaseBinarySensor):
    """Feeder food shortage problem sensor."""

    _attr_translation_key = "food_shortage"
    _attr_name = "缺粮告警"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:food-drumstick-off"

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize food shortage sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_food_shortage"

    @property
    def is_on(self) -> bool:
        """Return True if out of food."""
        return bool(self.coordinator.data.get("is_material_shortage"))


class VsonFeederWaterChangeDueBinarySensor(VsonFeederBaseBinarySensor):
    """Feeder water change due reminder sensor."""

    _attr_translation_key = "water_change_due"
    _attr_name = "换水到期提醒"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:water-alert"

    def __init__(self, coordinator: VsonFeederCoordinator) -> None:
        """Initialize water change due sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._mac}_water_change_due"

    @property
    def is_on(self) -> bool:
        """Return True if water change is needed."""
        return bool(self.coordinator.data.get("water_change_due"))
