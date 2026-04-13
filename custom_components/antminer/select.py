"""Select platform for the Antminer integration – mining mode control."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MINER_MODES, MODES_BY_NAME, MODES_LIST
from .coordinator import AntminerCoordinator
from .entity import AntminerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the mining mode select entity."""
    coordinator: AntminerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AntminerModeSelect(coordinator, entry.entry_id)])


class AntminerModeSelect(AntminerEntity, SelectEntity):
    """Select entity that controls the miner's operating mode.

    Maps between the display names (Normal / Sleep / High Performance) and
    the integer values understood by the miner's CGI API.
    """

    _attr_options = MODES_LIST
    _attr_icon = "mdi:gauge"
    _attr_name = "Mining Mode"

    def __init__(self, coordinator: AntminerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_mode"

    @property
    def current_option(self) -> str | None:
        """Return the currently active mode as a display name."""
        if not self.coordinator.data:
            return None
        raw = str(
            self.coordinator.data["config"].get("bitmain-work-mode") or "0"
        )
        return MINER_MODES.get(raw, "Normal")

    async def async_select_option(self, option: str) -> None:
        """Apply the selected mode to the miner."""
        mode_int = int(MODES_BY_NAME.get(option, "0"))
        await self.coordinator.async_apply_settings(**{"miner-mode": mode_int})
