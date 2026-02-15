"""Config flow for avalon_miner integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_HOST

from .api import AvalonMinerApiClient, AvalonMinerApiCommunicationError
from .const import (
    CONF_POLLING_INTERVAL,
    CONF_PORT,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_POLLING_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
    }
)


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class HeaterControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for avalon_miner."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self) -> None:
        """Initialize flow."""
        self._host: str | None = None
        self._port: int | None = None
        self._interval: int | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._port = user_input[CONF_PORT]
            self._interval = user_input[CONF_POLLING_INTERVAL]

            try:
                info = await self._validate_and_setup()

                await self.async_set_unique_id(info["dna"])
                self._abort_if_unique_id_configured(updates=user_input)

                user_input["dna"] = info["dna"]
                user_input["model"] = info["model"]
                user_input["firmware"] = info["firmware"]

                return self.async_create_entry(
                    title=f"{info['model']} ({info['dna']})",
                    data=user_input,
                )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def _validate_and_setup(self) -> dict:
        """Validate the host and return device info."""
        client = AvalonMinerApiClient(
            host=self._host,
            port=self._port,
        )

        try:
            version_resp = await client.async_get_version()
        except AvalonMinerApiCommunicationError as exc:
            raise CannotConnect from exc

        ver_list = version_resp.get("VERSION", [])
        if not ver_list:
            raise CannotConnect

        ver = ver_list[0] if isinstance(ver_list, list) else ver_list
        dna = ver.get("DNA", "")
        if not dna:
            raise CannotConnect

        return {
            "dna": dna,
            "model": ver.get("MODEL", "Unknown"),
            "firmware": ver.get(
                "LVERSION",
                ver.get("BVERSION", ver.get("CGVERSION", "")),
            ),
        }
