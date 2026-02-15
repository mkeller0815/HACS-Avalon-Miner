"""Custom types for avalon_miner."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import AvalonMinerApiClient
    from .coordinator import AvalonMinerDataUpdateCoordinator


type AvalonMinerConfigEntry = ConfigEntry[AvalonMinerData]


@dataclass
class AvalonMinerData:
    """Data for the integration."""

    client: AvalonMinerApiClient
    coordinator: AvalonMinerDataUpdateCoordinator
    integration: Integration
