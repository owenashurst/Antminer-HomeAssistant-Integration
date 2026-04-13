"""Data update coordinator for the Antminer integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import httpx

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class AntminerCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator that fetches summary and config data from the Antminer CGI API."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        username: str,
        password: str,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._base_url = f"http://{host}:{port}"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _auth(self) -> httpx.DigestAuth:
        return httpx.DigestAuth(self.username, self.password)

    # ------------------------------------------------------------------
    # DataUpdateCoordinator interface
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict:
        """Fetch summary and configuration from the miner."""
        auth = self._auth()
        timeout = httpx.Timeout(10.0)
        try:
            async with httpx.AsyncClient(auth=auth, timeout=timeout) as client:
                resp = await client.get(f"{self._base_url}/cgi-bin/summary.cgi")
                resp.raise_for_status()
                summary = resp.json()

                resp = await client.get(f"{self._base_url}/cgi-bin/get_miner_conf.cgi")
                resp.raise_for_status()
                config = resp.json()

        except httpx.HTTPStatusError as err:
            raise UpdateFailed(
                f"HTTP {err.response.status_code} error from Antminer at {self._base_url}"
            ) from err
        except httpx.RequestError as err:
            raise UpdateFailed(
                f"Connection error communicating with Antminer: {err}"
            ) from err

        return {"summary": summary, "config": config}

    # ------------------------------------------------------------------
    # Settings helpers
    # ------------------------------------------------------------------

    async def async_apply_settings(self, **overrides: object) -> None:
        """POST updated settings to the miner, merging with the current config.

        The GET endpoint uses different field names (bitmain-work-mode) from
        the POST endpoint (miner-mode), so we normalise here.

        Any keyword argument passed as *overrides* is merged on top of the
        current values before posting, allowing callers to change only the
        fields they care about.
        """
        if not self.data:
            raise RuntimeError(
                "Cannot apply settings: coordinator has no data yet."
            )

        current: dict = self.data["config"]

        # Build a POST payload from the current GET values, translating
        # field names where needed.
        payload: dict = {
            "bitmain-fan-ctrl": current.get("bitmain-fan-ctrl", False),
            "bitmain-fan-pwm": str(current.get("bitmain-fan-pwm", "100") or "100"),
            "bitmain-hashrate-percent": str(
                current.get("bitmain-hashrate-percent") or "100"
            ),
            # bitmain-work-mode (GET) → miner-mode (POST), must be an integer
            "miner-mode": int(current.get("bitmain-work-mode") or 0),
            "pools": current.get("pools", []),
        }

        payload.update(overrides)

        auth = self._auth()
        timeout = httpx.Timeout(10.0)
        try:
            async with httpx.AsyncClient(auth=auth, timeout=timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/cgi-bin/set_miner_conf.cgi",
                    json=payload,
                )
                # The Antminer returns 200 with {"stats":"success"} on success.
                # Only hard-fail on 5xx server errors; the miner sometimes returns
                # non-standard codes on 4xx that still mean "accepted".
                if resp.status_code >= 500:
                    resp.raise_for_status()
        except httpx.HTTPStatusError as err:
            _LOGGER.error(
                "Failed to apply settings – HTTP %s", err.response.status_code
            )
            raise RuntimeError(
                f"Failed to apply settings – HTTP {err.response.status_code}"
            ) from err
        except httpx.RequestError as err:
            _LOGGER.error("Failed to apply settings – %s", err)
            raise RuntimeError(f"Failed to apply settings – {err}") from err

        # The miner needs a few seconds to apply new settings before it will
        # respond correctly to poll requests.  Schedule the refresh on the
        # event loop after a short delay so it doesn't race against the
        # miner's internal restart.
        async def _delayed_refresh() -> None:
            await asyncio.sleep(5)
            await self.async_request_refresh()

        self.hass.async_create_task(_delayed_refresh())
