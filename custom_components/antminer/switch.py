"""Switch platform for the Antminer integration – manual fan control toggle."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AntminerCoordinator
from .entity import AntminerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the manual fan control switch entity."""
    coordinator: AntminerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AntminerFanControlSwitch(coordinator, entry.entry_id)])


class AntminerFanControlSwitch(AntminerEntity, SwitchEntity):
    """Switch entity that toggles between automatic and manual fan control.

    ON  → bitmain-fan-ctrl = true  (manual PWM; Fan Speed number entity is active)
    OFF → bitmain-fan-ctrl = false (miner auto-controls fans based on temperature)
    """

    _attr_icon = "mdi:fan-auto"
    _attr_name = "Manual Fan Control"

    def __init__(self, coordinator: AntminerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_fan_manual_control"

    @property
    def is_on(self) -> bool:
        """Return True when manual fan control is active."""
        if not self.coordinator.data:
            return False
        return bool(
            self.coordinator.data["config"].get("bitmain-fan-ctrl", False)
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable manual fan control."""
        await self.coordinator.async_apply_settings(**{"bitmain-fan-ctrl": True})

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable manual fan control (return to automatic)."""
        await self.coordinator.async_apply_settings(**{"bitmain-fan-ctrl": False})
