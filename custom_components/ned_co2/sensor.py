from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_UNIT
from .coordinator import NedCo2Coordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: NedCo2Coordinator = hass.data[DOMAIN][entry.entry_id]
    unit_pref = entry.data.get(CONF_UNIT, "g_per_kwh")

    entities: list[SensorEntity] = [
        NedCo2CurrentSensor(coordinator, entry.entry_id, unit_pref),
        NedCo2MinWindowSensor(coordinator, entry.entry_id, unit_pref),
    ]
    async_add_entities(entities)

class NedCo2Base(CoordinatorEntity[NedCo2Coordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: NedCo2Coordinator, entry_id: str, unit_pref: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._unit_pref = unit_pref
        self._attr_native_unit_of_measurement = "g/kWh" if unit_pref == "g_per_kwh" else "kg/kWh"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "NED CO₂ intensiteit",
            "manufacturer": "Nationaal Energie Dashboard",
            "model": "utilizations",
        }

    def _convert(self, kg_per_kwh: float) -> float:
        return round(kg_per_kwh * 1000.0, 0) if self._unit_pref == "g_per_kwh" else round(kg_per_kwh, 4)

class NedCo2CurrentSensor(NedCo2Base):
    _attr_name = "CO₂ intensiteit (nu/volgende periode)"
    _attr_unique_id = None

    def __init__(self, coordinator: NedCo2Coordinator, entry_id: str, unit_pref: str) -> None:
        super().__init__(coordinator, entry_id, unit_pref)
        self._attr_unique_id = f"{entry_id}_current"

    @property
    def native_value(self) -> float | None:
        current = (self.coordinator.data or {}).get("current")
        if not current:
            return None
        return self._convert(current["emissionfactor_kg_per_kwh"])

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        data = self.coordinator.data or {}
        series = data.get("series", [])
        out = []
        for r in series:
            ts = dt_util.parse_datetime(r["validfrom"]) if r.get("validfrom") else None
            ts_local = ts.astimezone(dt_util.DEFAULT_TIME_ZONE) if ts else None
            out.append({
                "t": ts_local.isoformat() if ts_local else r.get("validfrom"),
                "g_per_kwh": round(r["emissionfactor_g_per_kwh"], 1),
            })
        return {
            "points": out,
            "count": data.get("meta", {}).get("count", 0),
            "fetched_at": data.get("meta", {}).get("fetched_at"),
        }

class NedCo2MinWindowSensor(NedCo2Base):
    _attr_name = "CO₂ minimum (venster)"
    _attr_unique_id = None

    def __init__(self, coordinator: NedCo2Coordinator, entry_id: str, unit_pref: str) -> None:
        super().__init__(coordinator, entry_id, unit_pref)
        self._attr_unique_id = f"{entry_id}_min"

    @property
    def native_value(self) -> float | None:
        min_item = (self.coordinator.data or {}).get("min_item")
        if not min_item:
            return None
        return self._convert(min_item["emissionfactor_kg_per_kwh"])

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        min_item = (self.coordinator.data or {}).get("min_item")
        if not min_item:
            return None
        ts = dt_util.parse_datetime(min_item.get("validfrom")) if min_item.get("validfrom") else None
        ts_local = ts.astimezone(dt_util.DEFAULT_TIME_ZONE) if ts else None
        return {
            "at": ts_local.isoformat() if ts_local else min_item.get("validfrom")
        }
