"""DataUpdateCoordinator for VSON Fish Feeder."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import VsonFeederApiClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class VsonFeederCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage fetching data from VSON Feeder API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: VsonFeederApiClient,
        mac: str,
    ) -> None:
        """Initialize coordinator."""
        self.api = api
        self.mac = mac.strip().upper()

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.mac}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API and calculate processed metrics."""
        try:
            raw_data = await self.api.async_get_device_status(self.mac)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with VSON cloud: {err}") from err

        return self._process_data(raw_data)

    def _process_data(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Parse and enrich raw device state."""
        dev_type = raw.get("_device_type")
        version = raw.get("version", "")
        if not dev_type:
            dev_type = "8621" if (self.mac.startswith("86:21") or "8621" in version) else "8615"

        model = "WP8621N" if dev_type == "8621" else "WP8615"

        # Battery (present on WP8615)
        battery_percent: int | None = None
        battery_bars: int | None = None
        if "battery" in raw:
            battery_bars = int(raw.get("battery", 3))
            if battery_bars == 0:
                battery_percent = 5
            elif battery_bars == 1:
                battery_percent = 33
            elif battery_bars == 2:
                battery_percent = 66
            else:
                battery_percent = 100

        # Charging & power (WP8615)
        is_charging: bool | None = None
        if "isCharging" in raw:
            is_charging = str(raw.get("isCharging", "0")) == "1"

        power_plugged: bool | None = None
        if "powerState" in raw:
            power_plugged = int(raw.get("powerState", 0)) == 1

        equipment_state = int(raw.get("equipmentState", 0))
        is_material = str(raw.get("isMaterial", "0")) == "1"
        period = int(raw.get("period", 7))
        change_water_time = raw.get("changeWaterTime")

        # Feeding timestamps
        last_time_l = raw.get("lastTimeL")
        last_time_r = raw.get("lastTimeR")
        single_time = raw.get("time")

        # Pump (WP8621)
        has_pump = "isPump" in raw
        is_pump = str(raw.get("isPump", "0")) == "1" if has_pump else False

        # Cleanliness & water change due calculation
        water_cleanliness = 100.0
        water_change_due = False
        elapsed_days = 0.0

        if change_water_time and change_water_time != "2000-00-00 00:00:00":
            try:
                dt_change = datetime.strptime(change_water_time, "%Y-%m-%d %H:%M:%S")
                diff_sec = (datetime.now() - dt_change).total_seconds()
                if diff_sec > 0:
                    elapsed_days = diff_sec / 86400.0
                if period > 0:
                    fraction_remaining = 1.0 - (elapsed_days / float(period))
                    water_cleanliness = max(0.0, min(100.0, fraction_remaining * 100.0))
                    if water_cleanliness <= 1.0 or elapsed_days >= period:
                        water_change_due = True
            except Exception as e:
                _LOGGER.warning("Could not parse changeWaterTime '%s': %s", change_water_time, e)

        return {
            "mac": self.mac,
            "device_type": dev_type,
            "model": model,
            "version": version or model,
            "is_online": equipment_state == 0,
            "battery_bars": battery_bars,
            "battery_percent": battery_percent,
            "is_charging": is_charging,
            "power_plugged": power_plugged,
            "is_material_shortage": is_material,
            "period_days": period,
            "change_water_time": change_water_time,
            "elapsed_water_change_days": round(elapsed_days, 1),
            "water_cleanliness": round(water_cleanliness, 1),
            "water_change_due": water_change_due,
            "last_feed_time_left": last_time_l if last_time_l and last_time_l != "2000-00-00 00:00:00" else None,
            "last_feed_time_right": last_time_r if last_time_r and last_time_r != "2000-00-00 00:00:00" else None,
            "last_feed_time": single_time if single_time and single_time != "2000-00-00 00:00:00" else None,
            "has_pump": has_pump,
            "is_pump": is_pump,
        }
