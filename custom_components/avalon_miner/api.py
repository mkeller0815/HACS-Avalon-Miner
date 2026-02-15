"""Avalon Miner async TCP API Client."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from .const import LOGGER


class AvalonMinerApiError(Exception):
    """Exception to indicate a general API error."""


class AvalonMinerApiCommunicationError(AvalonMinerApiError):
    """Exception to indicate a communication error."""


def parse_estats_field(mm_id0: str, field_name: str) -> str | None:
    """Parse a field from the MM ID0 string in ESTATS response."""
    pattern = rf"{field_name}\[([^\]]+)\]"
    match = re.search(pattern, mm_id0)
    return match.group(1) if match else None


class AvalonMinerApiClient:
    """Async TCP API Client for Avalon Miners."""

    def __init__(self, host: str, port: int = 4028, timeout: int = 5) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout

    async def async_send_command(
        self, command: str, params: str = ""
    ) -> dict[str, Any]:
        """Send a command to the miner API via async TCP."""
        if params:
            json_cmd = json.dumps(
                {"command": command, "parameter": params}, separators=(",", ":")
            )
        else:
            json_cmd = json.dumps({"command": command}, separators=(",", ":"))

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=self._timeout,
            )

            writer.write(json_cmd.encode("utf-8"))
            await writer.drain()

            response = b""
            try:
                while True:
                    chunk = await asyncio.wait_for(
                        reader.read(4096), timeout=self._timeout
                    )
                    if not chunk:
                        break
                    response += chunk
            except asyncio.TimeoutError:
                pass

            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

            response_str = response.decode("utf-8").rstrip("\x00").strip()
            return json.loads(response_str)

        except asyncio.TimeoutError as exc:
            msg = f"Timeout connecting to {self._host}:{self._port}"
            raise AvalonMinerApiCommunicationError(msg) from exc
        except OSError as exc:
            msg = f"Error communicating with {self._host}:{self._port} - {exc}"
            raise AvalonMinerApiCommunicationError(msg) from exc
        except json.JSONDecodeError as exc:
            msg = f"Invalid JSON response from {self._host}:{self._port} - {exc}"
            raise AvalonMinerApiCommunicationError(msg) from exc
        except AvalonMinerApiError:
            raise
        except Exception as exc:
            msg = f"Unexpected error communicating with miner: {exc}"
            raise AvalonMinerApiError(msg) from exc

    async def async_get_version(self) -> dict[str, Any]:
        """Get miner version information."""
        return await self.async_send_command("version")

    async def async_get_summary(self) -> dict[str, Any]:
        """Get miner summary statistics."""
        return await self.async_send_command("summary")

    async def async_get_estats(self) -> dict[str, Any]:
        """Get extended miner statistics."""
        return await self.async_send_command("estats")

    async def async_get_pools(self) -> dict[str, Any]:
        """Get pool information."""
        return await self.async_send_command("pools")

    async def async_get_lcd(self) -> dict[str, Any]:
        """Get LCD/active pool information."""
        return await self.async_send_command("lcd")

    async def async_fetch_all_data(self) -> dict[str, Any]:
        """Fetch all data from the miner in parallel."""
        version_task = self.async_get_version()
        summary_task = self.async_get_summary()
        estats_task = self.async_get_estats()
        pools_task = self.async_get_pools()
        lcd_task = self.async_get_lcd()

        results = await asyncio.gather(
            version_task, summary_task, estats_task, pools_task, lcd_task,
            return_exceptions=True,
        )

        data: dict[str, Any] = {}

        # Version
        version_resp = results[0]
        if isinstance(version_resp, Exception):
            raise AvalonMinerApiCommunicationError(
                f"Failed to get version: {version_resp}"
            ) from version_resp
        ver_list = version_resp.get("VERSION", [])
        ver = ver_list[0] if isinstance(ver_list, list) and ver_list else {}
        data["model"] = ver.get("MODEL", "Unknown")
        data["dna"] = ver.get("DNA", "unknown")
        data["prod"] = ver.get("PROD", "")
        data["mac"] = ver.get("MAC", "")
        data["firmware"] = ver.get(
            "LVERSION", ver.get("BVERSION", ver.get("CGVERSION", ""))
        )

        # Summary
        summary_resp = results[1]
        if not isinstance(summary_resp, Exception):
            sum_list = summary_resp.get("SUMMARY", [])
            summary = (
                sum_list[0] if isinstance(sum_list, list) and sum_list else {}
            )
            data["hashrate_5s"] = summary.get("MHS 5s", 0)
            data["hashrate_1m"] = summary.get("MHS 1m", 0)
            data["hashrate_5m"] = summary.get("MHS 5m", 0)
            data["hashrate_15m"] = summary.get("MHS 15m", 0)
            data["accepted_shares"] = summary.get("Accepted", 0)
            data["rejected_shares"] = summary.get("Rejected", 0)
            data["hardware_errors"] = summary.get("Hardware Errors", 0)
            data["best_share"] = summary.get("Best Share", 0)
            data["found_blocks"] = summary.get("Found Blocks", 0)
        else:
            LOGGER.warning("Failed to get summary: %s", summary_resp)

        # ESTATS
        estats_resp = results[2]
        if not isinstance(estats_resp, Exception):
            stats_list = estats_resp.get("STATS", [])
            stats = (
                stats_list[0]
                if isinstance(stats_list, list) and stats_list
                else {}
            )
            data["elapsed"] = stats.get("Elapsed", 0)
            mm_id0 = stats.get("MM ID0", "")
            data["mm_id0"] = mm_id0

            if mm_id0:
                data["soft_off"] = parse_estats_field(mm_id0, "SoftOFF")
                data["work_mode"] = parse_estats_field(mm_id0, "WORKMODE")
                data["temp_avg"] = parse_estats_field(mm_id0, "TAvg")
                data["temp_max"] = parse_estats_field(mm_id0, "TMax")
                data["temp_inlet"] = parse_estats_field(mm_id0, "ITemp")
                data["temp_target"] = parse_estats_field(mm_id0, "TarT")
                data["temp_hb_inlet"] = parse_estats_field(mm_id0, "HBITemp")
                data["temp_hb_outlet"] = parse_estats_field(mm_id0, "HBOTemp")
                data["fan_speed_pct"] = parse_estats_field(mm_id0, "FanR")
                data["fan1_rpm"] = parse_estats_field(mm_id0, "Fan1")
                data["fan2_rpm"] = parse_estats_field(mm_id0, "Fan2")
                data["fan3_rpm"] = parse_estats_field(mm_id0, "Fan3")
                data["fan4_rpm"] = parse_estats_field(mm_id0, "Fan4")
                data["power_output"] = parse_estats_field(mm_id0, "MPO")
                data["ghs_avg"] = parse_estats_field(mm_id0, "GHSavg")
                data["ghs_spd"] = parse_estats_field(mm_id0, "GHSspd")
        else:
            LOGGER.warning("Failed to get estats: %s", estats_resp)

        # Pools
        pools_resp = results[3]
        if not isinstance(pools_resp, Exception):
            pools_list = pools_resp.get("POOLS", [])
            data["pools"] = pools_list
        else:
            LOGGER.warning("Failed to get pools: %s", pools_resp)
            data["pools"] = []

        # LCD
        lcd_resp = results[4]
        if not isinstance(lcd_resp, Exception):
            lcd_list = lcd_resp.get("LCD", [])
            lcd = lcd_list[0] if isinstance(lcd_list, list) and lcd_list else {}
            data["current_pool"] = lcd.get("Current Pool", "")
            data["pool_user"] = lcd.get("User", "")
        else:
            LOGGER.warning("Failed to get lcd: %s", lcd_resp)

        return data

    async def async_set_fan_speed(self, value: int) -> None:
        """Set fan speed. 0 = Auto, 25-100 = fixed percentage."""
        if value == 0:
            params = "0,fan-spd,-1"
        else:
            params = f"0,fan-spd,{value}"
        await self.async_send_command("ascset", params)

    async def async_set_work_mode(self, mode: str) -> None:
        """Set work mode. 0=Eco, 1=Standard, 2=Super."""
        await self.async_send_command("ascset", f"0,workmode,set,{mode}")

    async def async_set_target_temp(self, temp: int) -> None:
        """Set target temperature (50-90)."""
        await self.async_send_command("ascset", f"0,target-temp,{temp}")

    async def async_reboot(self) -> None:
        """Reboot the miner."""
        await self.async_send_command("ascset", "0,reboot,0")

    async def async_reset_filter_clean(self) -> None:
        """Reset filter clean reminder."""
        await self.async_send_command("ascset", "0,filter-clean,1")
