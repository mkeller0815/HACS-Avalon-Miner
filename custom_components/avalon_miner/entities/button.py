"""Button platform for avalon_miner."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)

from ..const import DOMAIN
from ..entity import AvalonMinerEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..coordinator import AvalonMinerDataUpdateCoordinator
    from ..data import AvalonMinerConfigEntry

ENTITY_DESCRIPTIONS = (
    ButtonEntityDescription(
        key="reboot",
        icon="mdi:restart",
        entity_registry_enabled_default=True,
        device_class=ButtonDeviceClass.RESTART,
    ),
    ButtonEntityDescription(
        key="reset_filter",
        icon="mdi:air-filter",
        entity_registry_enabled_default=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AvalonMinerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    async_add_entities(
        AvalonMinerButton(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class AvalonMinerButton(AvalonMinerEntity, ButtonEntity):
    """AvalonMinerButton class."""

    def __init__(
        self,
        coordinator: AvalonMinerDataUpdateCoordinator,
        entity_description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_translation_key = entity_description.key
        self._attr_unique_id = (
            f"{self.coordinator.device}_{entity_description.key}"
        )

    @property
    def available(self) -> bool:
        """Return the availability."""
        return self.coordinator.last_update_success

    async def async_press(self) -> None:
        """Handle the button press."""
        if self.entity_description.key == "reboot":
            await self.coordinator.entry.runtime_data.client.async_reboot()
        elif self.entity_description.key == "reset_filter":
            await self.coordinator.entry.runtime_data.client.async_reset_filter_clean()
