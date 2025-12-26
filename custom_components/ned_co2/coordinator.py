from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from aiohttp import ClientSession, ClientResponseError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CONF_API_KEY, CONF_POINT, CONF_TYPE, CONF_ACTIVITY, CONF_CLASSIFICATION,
    CONF_GRANULARITY, CONF_GRAN_TZ, CONF_LOOKAHEAD_HOURS, CONF_UPDATE_INTERVAL_MIN,
    CONF_UNIT, DEFAULTS
)

_LOGGER = logging.getLogger(__name__)
BASE_URL = "https://api.ned.nl/v1/utilizations"

def _as_utc_iso(dt: datetime) -> str:
    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z")

class NedCo2Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, session: ClientSession, config: dict[str, Any]) -> None:
        self.hass = hass
        self.session = session
        self.config = {**DEFAULTS, **config}
        interval = timedelta(minutes=int(self.config.get(CONF_UPDATE_INTERVAL_MIN, DEFAULTS[CONF_UPDATE_INTERVAL_MIN])))
        super().__init__(
            hass,
            _LOGGER,
            name="NED CO2 Coordinator",
            update_interval=interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        params = self._build_params()
        headers = {
            "X-AUTH-TOKEN": self.config[CONF_API_KEY],
            "Accept": "application/ld+json",
        }

        try:
            async with self.session.get(BASE_URL, params=params, headers=headers, allow_redirects=False) as resp:
                if resp.status in (401, 403):
                    raise UpdateFailed("Unauthorized/Forbidden: check API key and access.")
                if resp.status == 429:
                    await asyncio.sleep(5)
                    async with self.session.get(BASE_URL, params=params, headers=headers, allow_redirects=False) as resp2:
                        resp2.raise_for_status()
                        data = await resp2.json()
                else:
                    resp.raise_for_status()
                    data = await resp.json()
        except ClientResponseError as e:  # pragma: no cover
            status = getattr(e, "status", "")
            raise UpdateFailed(f"HTTP error: {status} {e}") from e
        except Exception as e:  # noqa: BLE001
            raise UpdateFailed(f"Unexpected error: {e}") from e

        items = data
        if isinstance(data, dict) and "hydra:member" in data:
            items = data.get("hydra:member", [])

        def _parse_item(it: dict[str, Any]) -> dict[str, Any]:
            kg_per_kwh = float(it.get("emissionfactor", 0.0))
            g_per_kwh = kg_per_kwh * 1000.0
            return {
                "id": it.get("id"),
                "validfrom": it.get("validfrom"),
                "validto": it.get("validto"),
                "emissionfactor_kg_per_kwh": kg_per_kwh,
                "emissionfactor_g_per_kwh": g_per_kwh,
                "lastupdate": it.get("lastupdate"),
            }

        series = sorted([_parse_item(x) for x in items], key=lambda r: r.get("validfrom") or "")

        now_utc = dt_util.utcnow()
        current = None
        for r in series:
            try:
                start = dt_util.parse_datetime(r["validfrom"])
                if start and start >= now_utc:
                    current = r
                    break
            except Exception:
                continue
        if current is None and series:
            current = series[-1]

        min_item = min(series, key=lambda r: r["emissionfactor_g_per_kwh"]) if series else None

        return {
            "series": series,
            "current": current,
            "min_item": min_item,
            "meta": {
                "params": params,
                "count": len(series),
                "fetched_at": _as_utc_iso(now_utc),
            },
        }

    def _build_params(self) -> dict[str, Any]:
        cfg = self.config
        now = dt_util.utcnow()
        end = now + timedelta(hours=int(cfg.get(CONF_LOOKAHEAD_HOURS, DEFAULTS[CONF_LOOKAHEAD_HOURS])))
        params = {
            "point": int(cfg[CONF_POINT]),
            "type": int(cfg[CONF_TYPE]),
            "activity": int(cfg[CONF_ACTIVITY]),
            "classification": int(cfg[CONF_CLASSIFICATION]),
            "granularity": int(cfg[CONF_GRANULARITY]),
            "granularitytimezone": int(cfg[CONF_GRAN_TZ]),
            "validfrom[after]": _as_utc_iso(now),
            "validfrom[strictly_before]": _as_utc_iso(end),
        }
        return params
