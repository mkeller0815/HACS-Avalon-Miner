"""The Avalon Miner integration."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, Platform
from homeassistant.loader import async_get_loaded_integration

from .api import AvalonMinerApiClient
from .const import CONF_POLLING_INTERVAL, CONF_PORT, DEFAULT_PORT, DOMAIN, LOGGER
from .coordinator import AvalonMinerDataUpdateCoordinator
from .data import AvalonMinerData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import AvalonMinerConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.BUTTON,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AvalonMinerConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = AvalonMinerDataUpdateCoordinator(
        hass=hass,
        entry=entry,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(seconds=entry.data[CONF_POLLING_INTERVAL]),
    )
    entry.runtime_data = AvalonMinerData(
        client=AvalonMinerApiClient(
            host=entry.data[CONF_HOST],
            port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: AvalonMinerConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: AvalonMinerConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
