"""Config flow for the Antminer integration."""
from __future__ import annotations

import logging

import httpx
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME

from .const import DEFAULT_PASSWORD, DEFAULT_PORT, DEFAULT_USERNAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


class AntminerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Antminer."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle the initial setup step shown to the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Prevent duplicate entries for the same host:port combination.
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
            )
            self._abort_if_unique_id_configured()

            try:
                await _test_connection(
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )
            except httpx.HTTPStatusError as err:
                errors["base"] = "invalid_auth" if err.response.status_code == 401 else "cannot_connect"
            except httpx.RequestError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during Antminer config flow")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"Antminer ({user_input[CONF_HOST]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                    vol.Optional(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
                }
            ),
            errors=errors,
        )


async def _test_connection(
    host: str, port: int, username: str, password: str
) -> None:
    """Verify that the miner is reachable and the credentials are valid."""
    auth = httpx.DigestAuth(username, password)
    async with httpx.AsyncClient(auth=auth, timeout=httpx.Timeout(10.0)) as client:
        resp = await client.get(f"http://{host}:{port}/cgi-bin/summary.cgi")
        resp.raise_for_status()
