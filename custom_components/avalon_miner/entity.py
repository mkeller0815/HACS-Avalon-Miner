"""Entity class for avalon_miner."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AvalonMinerDataUpdateCoordinator


class AvalonMinerEntity(CoordinatorEntity[AvalonMinerDataUpdateCoordinator]):
    """AvalonMinerEntity class."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AvalonMinerDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.entry.entry_id

    @property
    def device_info(self) -> dict:
        return self.coordinator.device_info
