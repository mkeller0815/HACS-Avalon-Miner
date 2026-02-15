"""Sensor platform for avalon_miner."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfPower,
    UnitOfTemperature,
)

from ..const import DOMAIN, WORK_MODE_MAP
from ..entity import AvalonMinerEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..coordinator import AvalonMinerDataUpdateCoordinator
    from ..data import AvalonMinerConfigEntry

ALWAYS_AVAILABLE_SENSORS = {"current_pool", "pool_user", "work_mode_display"}

ENTITY_DESCRIPTIONS = (
    # --- Hashrate ---
    SensorEntityDescription(
        key="hashrate_5s",
        icon="mdi:speedometer",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="TH/s",
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="hashrate_1m",
        icon="mdi:speedometer",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="TH/s",
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="hashrate_5m",
        icon="mdi:speedometer",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="TH/s",
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="hashrate_15m",
        icon="mdi:speedometer",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="TH/s",
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="hashrate_avg",
        icon="mdi:speedometer",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="TH/s",
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="hashrate_current",
        icon="mdi:speedometer",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="TH/s",
        suggested_display_precision=2,
    ),
    # --- Temperature ---
    SensorEntityDescription(
        key="temp_avg",
        icon="mdi:thermometer",
        entity_registry_enabled_default=True,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="temp_max",
        icon="mdi:thermometer-high",
        entity_registry_enabled_default=True,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="temp_inlet",
        icon="mdi:thermometer-low",
        entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="temp_target",
        icon="mdi:thermometer-auto",
        entity_registry_enabled_default=True,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="temp_hb_inlet",
        icon="mdi:thermometer-low",
        entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="temp_hb_outlet",
        icon="mdi:thermometer-high",
        entity_registry_enabled_default=False,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=0,
    ),
    # --- Fan ---
    SensorEntityDescription(
        key="fan_speed_pct",
        icon="mdi:fan",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="fan1_rpm",
        icon="mdi:fan",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="RPM",
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="fan2_rpm",
        icon="mdi:fan",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="RPM",
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="fan3_rpm",
        icon="mdi:fan",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="RPM",
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="fan4_rpm",
        icon="mdi:fan",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="RPM",
        suggested_display_precision=0,
    ),
    # --- Power/Mining ---
    SensorEntityDescription(
        key="power_output",
        icon="mdi:flash",
        entity_registry_enabled_default=True,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="accepted_shares",
        icon="mdi:check-circle",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="rejected_shares",
        icon="mdi:close-circle",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="hardware_errors",
        icon="mdi:alert-circle",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="best_share",
        icon="mdi:trophy",
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="found_blocks",
        icon="mdi:cube",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    # --- Status/Info ---
    SensorEntityDescription(
        key="uptime",
        icon="mdi:clock-outline",
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="work_mode_display",
        icon="mdi:cog",
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="current_pool",
        icon="mdi:server-network",
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="pool_user",
        icon="mdi:account",
        entity_registry_enabled_default=True,
    ),
)


def _format_uptime(seconds: int) -> str:
    """Format uptime in human-readable format."""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def _safe_float(value: str | None) -> float | None:
    """Safely convert a string to float."""
    if value is None:
        return None
    try:
        val = float(value.replace("%", ""))
        return val if val != -273 else None
    except (ValueError, AttributeError):
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AvalonMinerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        AvalonMinerSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class AvalonMinerSensor(AvalonMinerEntity, SensorEntity):
    """AvalonMinerSensor class."""

    def __init__(
        self,
        coordinator: AvalonMinerDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_translation_key = entity_description.key
        self._attr_unique_id = (
            f"{self.coordinator.device}_{entity_description.key}"
        )

    @property
    def native_value(self) -> str | float | None:
        """Return the native value of the sensor."""
        key = self.entity_description.key
        data = self.coordinator.data

        if data is None:
            return None

        # Hashrate from summary (MHS → TH/s)
        if key in ("hashrate_5s", "hashrate_1m", "hashrate_5m", "hashrate_15m"):
            mhs = data.get(key, 0)
            if mhs:
                return float(mhs) / 1_000_000
            return None

        # Hashrate from estats (GHS → TH/s)
        if key == "hashrate_avg":
            ghs = data.get("ghs_avg")
            return float(ghs) / 1000 if ghs else None

        if key == "hashrate_current":
            ghs = data.get("ghs_spd")
            return float(ghs) / 1000 if ghs else None

        # Temperature sensors
        if key in (
            "temp_avg", "temp_max", "temp_inlet", "temp_target",
            "temp_hb_inlet", "temp_hb_outlet",
        ):
            return _safe_float(data.get(key))

        # Fan sensors
        if key == "fan_speed_pct":
            val = data.get("fan_speed_pct")
            return _safe_float(val)

        if key in ("fan1_rpm", "fan2_rpm", "fan3_rpm", "fan4_rpm"):
            return _safe_float(data.get(key))

        # Power
        if key == "power_output":
            return _safe_float(data.get("power_output"))

        # Mining stats (directly from summary)
        if key in (
            "accepted_shares", "rejected_shares", "hardware_errors",
            "best_share", "found_blocks",
        ):
            return data.get(key)

        # Uptime
        if key == "uptime":
            elapsed = data.get("elapsed", 0)
            return _format_uptime(elapsed) if elapsed else None

        # Work mode display
        if key == "work_mode_display":
            mode = data.get("work_mode")
            return WORK_MODE_MAP.get(mode, f"Unknown ({mode})") if mode else None

        # Pool info
        if key == "current_pool":
            return data.get("current_pool") or None

        if key == "pool_user":
            return data.get("pool_user") or None

        return None

    @property
    def available(self) -> bool:
        """Return the availability."""
        if (
            self.entity_description.key in ALWAYS_AVAILABLE_SENSORS
            or self.coordinator.device_is_running
        ):
            return self.coordinator.last_update_success
        return False
