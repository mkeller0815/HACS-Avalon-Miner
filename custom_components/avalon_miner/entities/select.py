"""Select platform for avalon_miner."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity, SelectEntityDescription

from ..const import DOMAIN, WORK_MODE_MAP, WORK_MODE_REVERSE_MAP
from ..entity import AvalonMinerEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..coordinator import AvalonMinerDataUpdateCoordinator
    from ..data import AvalonMinerConfigEntry

ENTITY_DESCRIPTIONS = (
    SelectEntityDescription(
        key="work_mode",
        icon="mdi:cog",
        entity_registry_enabled_default=True,
        options=list(WORK_MODE_MAP.values()),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AvalonMinerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    async_add_entities(
        AvalonMinerSelect(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class AvalonMinerSelect(AvalonMinerEntity, SelectEntity):
    """AvalonMinerSelect class."""

    def __init__(
        self,
        coordinator: AvalonMinerDataUpdateCoordinator,
        entity_description: SelectEntityDescription,
    ) -> None:
        """Initialize the select class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_translation_key = entity_description.key
        self._attr_unique_id = (
            f"{self.coordinator.device}_{entity_description.key}"
        )

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        data = self.coordinator.data
        if data is None:
            return None

        mode = data.get("work_mode")
        return WORK_MODE_MAP.get(mode) if mode else None

    @property
    def available(self) -> bool:
        """Return the availability."""
        if self.coordinator.device_is_running:
            return self.coordinator.last_update_success
        return False

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        mode_value = WORK_MODE_REVERSE_MAP.get(option)
        if mode_value is not None:
            await self.coordinator.async_set_work_mode(mode_value)
