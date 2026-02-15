"""DataUpdateCoordinator for avalon_miner."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import AvalonMinerApiError
from .const import DOMAIN, MANUFACTURER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import AvalonMinerConfigEntry


class AvalonMinerDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    entry: AvalonMinerConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: AvalonMinerConfigEntry,
        logger,
        name,
        update_interval,
    ):
        self.entry = entry
        self.device = entry.data["dna"]
        super().__init__(
            hass, logger=logger, name=name, update_interval=update_interval
        )

    @property
    def device_is_running(self) -> bool:
        """Return True if the miner is running (SoftOFF == 0)."""
        if self.data and self.data.get("soft_off") == "0":
            return self.last_update_success
        return False

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.data["dna"])},
            name=f"{MANUFACTURER} {self.entry.data['model']}",
            manufacturer=MANUFACTURER,
            model=self.entry.data["model"],
            sw_version=self.entry.data.get("firmware", ""),
            serial_number=self.entry.data["dna"],
        )

    async def async_set_fan_speed(self, value: int) -> None:
        """Set fan speed and refresh."""
        await self.entry.runtime_data.client.async_set_fan_speed(value)
        await self.async_refresh()

    async def async_set_work_mode(self, mode: str) -> None:
        """Set work mode and refresh."""
        await self.entry.runtime_data.client.async_set_work_mode(mode)
        await self.async_refresh()

    async def async_set_target_temp(self, temp: int) -> None:
        """Set target temperature and refresh."""
        await self.entry.runtime_data.client.async_set_target_temp(temp)
        await self.async_refresh()

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.entry.runtime_data.client.async_fetch_all_data()
        except AvalonMinerApiError as exception:
            raise UpdateFailed(exception) from exception
