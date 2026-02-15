"""Number platform for avalon_miner."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)

from ..const import DOMAIN, LOGGER
from ..entity import AvalonMinerEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..coordinator import AvalonMinerDataUpdateCoordinator
    from ..data import AvalonMinerConfigEntry

ENTITY_DESCRIPTIONS = (
    NumberEntityDescription(
        key="fan_speed",
        icon="mdi:fan",
        entity_registry_enabled_default=True,
        native_min_value=0,
        native_max_value=100,
        native_step=5,
        mode=NumberMode.SLIDER,
    ),
    NumberEntityDescription(
        key="target_temperature",
        icon="mdi:thermometer-auto",
        entity_registry_enabled_default=True,
        native_min_value=50,
        native_max_value=90,
        native_step=1,
        mode=NumberMode.SLIDER,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AvalonMinerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    async_add_entities(
        AvalonMinerNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class AvalonMinerNumber(AvalonMinerEntity, NumberEntity):
    """AvalonMinerNumber class."""

    def __init__(
        self,
        coordinator: AvalonMinerDataUpdateCoordinator,
        entity_description: NumberEntityDescription,
    ) -> None:
        """Initialize the number class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_translation_key = entity_description.key
        self._attr_unique_id = (
            f"{self.coordinator.device}_{entity_description.key}"
        )

    @property
    def native_value(self) -> float | None:
        """Return the native value of the number."""
        data = self.coordinator.data
        if data is None:
            return None

        if self.entity_description.key == "fan_speed":
            val = data.get("fan_speed_pct")
            if val is not None:
                try:
                    pct = float(val.replace("%", ""))
                    return pct
                except (ValueError, AttributeError):
                    return None
            return None

        if self.entity_description.key == "target_temperature":
            val = data.get("temp_target")
            if val is not None:
                try:
                    return float(val)
                except (ValueError, AttributeError):
                    return None
            return None

        return None

    @property
    def available(self) -> bool:
        """Return the availability."""
        if self.coordinator.device_is_running:
            return self.coordinator.last_update_success
        return False

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        if self.entity_description.key == "fan_speed":
            await self.coordinator.async_set_fan_speed(int(value))
        elif self.entity_description.key == "target_temperature":
            await self.coordinator.async_set_target_temp(int(value))
