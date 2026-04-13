"""Number platform for the Antminer integration – fan speed control."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
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
    """Set up the fan speed number entity."""
    coordinator: AntminerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AntminerFanSpeedNumber(coordinator, entry.entry_id)])


class AntminerFanSpeedNumber(AntminerEntity, NumberEntity):
    """Number entity that controls the fan PWM percentage.

    Setting this value via Home Assistant also enables manual fan control
    (bitmain-fan-ctrl = true) so the change takes effect immediately.
    To return to automatic fan control, use the Manual Fan Control switch.
    """

    _attr_native_min_value = 0.0
    _attr_native_max_value = 100.0
    _attr_native_step = 1.0
    _attr_mode = NumberMode.SLIDER
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:fan"
    _attr_name = "Fan Speed"

    def __init__(self, coordinator: AntminerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_fan_speed"

    @property
    def native_value(self) -> float | None:
        """Return the current fan PWM percentage."""
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data["config"].get("bitmain-fan-pwm", "100")
        try:
            return float(raw or 100)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set fan speed and enable manual fan control."""
        await self.coordinator.async_apply_settings(
            **{
                "bitmain-fan-pwm": str(int(value)),
                "bitmain-fan-ctrl": True,
            }
        )
