"""Constants for avalon_miner."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "avalon_miner"
TITLE = "Avalon Miner"
MANUFACTURER = "Canaan"

DEFAULT_PORT = 4028
DEFAULT_SCAN_INTERVAL = 30

CONF_PORT = "port"
CONF_POLLING_INTERVAL = "polling_interval"

WORK_MODE_MAP = {
    "0": "Eco",
    "1": "Standard",
    "2": "Super",
}

WORK_MODE_REVERSE_MAP = {v: k for k, v in WORK_MODE_MAP.items()}
