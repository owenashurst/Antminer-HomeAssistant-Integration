"""Sensor platform for the Antminer integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AntminerCoordinator
from .entity import AntminerEntity


@dataclass(frozen=True)
class AntminerSensorEntityDescription(SensorEntityDescription):
    """Extends SensorEntityDescription with a value accessor."""

    value_fn: Callable[[dict], Any] | None = None


# ---------------------------------------------------------------------------
# Helper accessors
# ---------------------------------------------------------------------------

def _summary0(data: dict) -> dict:
    """Return the first (and normally only) SUMMARY entry."""
    return data["summary"]["SUMMARY"][0]


def _ths(data: dict, key: str) -> float:
    """Convert a GH/s value from the summary to TH/s, rounded to 3 d.p."""
    return round(_summary0(data)[key] / 1000, 3)


# ---------------------------------------------------------------------------
# Sensor descriptions
# ---------------------------------------------------------------------------

SENSOR_DESCRIPTIONS: tuple[AntminerSensorEntityDescription, ...] = (
    AntminerSensorEntityDescription(
        key="hashrate_5s",
        name="Hashrate (5s)",
        icon="mdi:pickaxe",
        native_unit_of_measurement="TH/s",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _ths(data, "rate_5s"),
    ),
    AntminerSensorEntityDescription(
        key="hashrate_30m",
        name="Hashrate (30m avg)",
        icon="mdi:pickaxe",
        native_unit_of_measurement="TH/s",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _ths(data, "rate_30m"),
    ),
    AntminerSensorEntityDescription(
        key="hashrate_avg",
        name="Hashrate (average)",
        icon="mdi:pickaxe",
        native_unit_of_measurement="TH/s",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _ths(data, "rate_avg"),
    ),
    AntminerSensorEntityDescription(
        key="hashrate_ideal",
        name="Ideal Hashrate",
        icon="mdi:pickaxe",
        native_unit_of_measurement="TH/s",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _ths(data, "rate_ideal"),
    ),
    AntminerSensorEntityDescription(
        key="running_time",
        name="Running Time",
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: _summary0(data)["elapsed"],
    ),
    AntminerSensorEntityDescription(
        key="hw_errors",
        name="HW Errors",
        icon="mdi:alert-circle-outline",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: _summary0(data)["hw_all"],
    ),
    AntminerSensorEntityDescription(
        key="best_share",
        name="Best Share",
        icon="mdi:trophy-outline",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _summary0(data)["bestshare"],
    ),
    AntminerSensorEntityDescription(
        key="miner_type",
        name="Miner Type",
        icon="mdi:chip",
        value_fn=lambda data: data["summary"]["INFO"].get("type"),
    ),
)


# ---------------------------------------------------------------------------
# Platform setup
# ---------------------------------------------------------------------------

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Antminer sensors from a config entry."""
    coordinator: AntminerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        AntminerSensorEntity(coordinator, entry.entry_id, description)
        for description in SENSOR_DESCRIPTIONS
    )


# ---------------------------------------------------------------------------
# Entity class
# ---------------------------------------------------------------------------

class AntminerSensorEntity(AntminerEntity, SensorEntity):
    """Representation of a single Antminer sensor."""

    entity_description: AntminerSensorEntityDescription

    def __init__(
        self,
        coordinator: AntminerCoordinator,
        entry_id: str,
        description: AntminerSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, entry_id)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the sensor value, or None if data is unavailable."""
        if not self.coordinator.data or self.entity_description.value_fn is None:
            return None
        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except (KeyError, IndexError, TypeError, ZeroDivisionError):
            return None
