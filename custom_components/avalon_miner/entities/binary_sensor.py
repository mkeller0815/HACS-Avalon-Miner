"""Binary sensor platform for avalon_miner."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from ..const import DOMAIN
from ..entity import AvalonMinerEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..coordinator import AvalonMinerDataUpdateCoordinator
    from ..data import AvalonMinerConfigEntry

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="miner_running",
        icon="mdi:pickaxe",
        entity_registry_enabled_default=True,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    BinarySensorEntityDescription(
        key="pool_connected",
        icon="mdi:server-network",
        entity_registry_enabled_default=True,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AvalonMinerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    async_add_entities(
        AvalonMinerBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class AvalonMinerBinarySensor(AvalonMinerEntity, BinarySensorEntity):
    """AvalonMinerBinarySensor class."""

    def __init__(
        self,
        coordinator: AvalonMinerDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_translation_key = entity_description.key
        self._attr_unique_id = (
            f"{self.coordinator.device}_{entity_description.key}"
        )

    @property
    def is_on(self) -> bool | None:
        """Return the native value of the binary sensor."""
        data = self.coordinator.data
        if data is None:
            return None

        if self.entity_description.key == "miner_running":
            return data.get("soft_off") == "0"

        if self.entity_description.key == "pool_connected":
            pools = data.get("pools", [])
            if pools:
                return pools[0].get("Status") == "Alive"
            return False

        return None

    @property
    def available(self) -> bool:
        """Return the availability."""
        return self.coordinator.last_update_success
