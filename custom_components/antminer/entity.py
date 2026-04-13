"""Shared base entity class for the Antminer integration."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AntminerCoordinator


class AntminerEntity(CoordinatorEntity[AntminerCoordinator]):
    """Base class for all Antminer entities.

    Sets _attr_has_entity_name = True so that each entity's name is
    automatically prefixed with the device name in the UI.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator: AntminerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information for this entity."""
        miner_info: dict = {}
        if self.coordinator.data:
            miner_info = self.coordinator.data.get("summary", {}).get("INFO", {})
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=miner_info.get("type", "Antminer"),
            manufacturer="Bitmain",
            model=miner_info.get("type", "Antminer"),
            sw_version=miner_info.get("miner_version"),
        )
