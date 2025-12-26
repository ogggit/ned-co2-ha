from __future__ import annotations

from typing import Any

import voluptuous as vol
from aiohttp import ClientSession
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import aiohttp_client

from .const import (
    DOMAIN, DEFAULTS,
    CONF_API_KEY, CONF_POINT, CONF_TYPE, CONF_ACTIVITY, CONF_CLASSIFICATION,
    CONF_GRANULARITY, CONF_GRAN_TZ, CONF_LOOKAHEAD_HOURS, CONF_UPDATE_INTERVAL_MIN, CONF_UNIT
)

from datetime import datetime, timedelta, timezone

BASE_URL = "https://api.ned.nl/v1/utilizations"

def _iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

async def _validate_api(hass: HomeAssistant, data: dict[str, Any]) -> None:
    session: ClientSession = aiohttp_client.async_get_clientsession(hass)
    now = datetime.now(timezone.utc)
    params = {
        "point": int(data[CONF_POINT]),
        "type": int(data[CONF_TYPE]),
        "activity": int(data[CONF_ACTIVITY]),
        "classification": int(data[CONF_CLASSIFICATION]),
        "granularity": int(data[CONF_GRANULARITY]),
        "granularitytimezone": int(data[CONF_GRAN_TZ]),
        "validfrom[after]": _iso_z(now),
        "validfrom[strictly_before]": _iso_z(now + timedelta(hours=1)),
    }
    headers = {"X-AUTH-TOKEN": data[CONF_API_KEY], "Accept": "application/ld+json"}
    async with session.get(BASE_URL, params=params, headers=headers, allow_redirects=False) as resp:
        if resp.status in (401, 403):
            raise ValueError("auth")
        if resp.status >= 400:
            raise ValueError(f"http_{resp.status}")

class NedCo2ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await _validate_api(self.hass, user_input)
                await self.async_set_unique_id(f"ned_co2_{user_input[CONF_POINT]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="NED CO₂ intensiteit", data=user_input)
            except ValueError as e:
                errors["base"] = "auth" if str(e) == "auth" else "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Required(CONF_POINT, default=DEFAULTS[CONF_POINT]): int,
            vol.Required(CONF_TYPE, default=DEFAULTS[CONF_TYPE]): int,
            vol.Required(CONF_ACTIVITY, default=DEFAULTS[CONF_ACTIVITY]): int,
            vol.Required(CONF_CLASSIFICATION, default=DEFAULTS[CONF_CLASSIFICATION]): vol.In([1, 2, 3]),
            vol.Required(CONF_GRANULARITY, default=DEFAULTS[CONF_GRANULARITY]): vol.In([4, 5, 6]),
            vol.Required(CONF_GRAN_TZ, default=DEFAULTS[CONF_GRAN_TZ]): int,
            vol.Required(CONF_LOOKAHEAD_HOURS, default=DEFAULTS[CONF_LOOKAHEAD_HOURS]): vol.All(int, vol.Range(min=1, max=168)),
            vol.Required(CONF_UPDATE_INTERVAL_MIN, default=DEFAULTS[CONF_UPDATE_INTERVAL_MIN]): vol.All(int, vol.Range(min=5, max=1440)),
            vol.Required(CONF_UNIT, default=DEFAULTS[CONF_UNIT]): vol.In(["g_per_kwh", "kg_per_kwh"]),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, user_input: dict[str, Any] | None = None):
        return await self.async_step_user(user_input)

    async def async_step_options(self, user_input: dict[str, Any] | None = None):
        return await self.async_step_user(user_input)

class NedCo2OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        return await self.async_step_edit(user_input)

    async def async_step_edit(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        data = {**self.config_entry.data, **(user_input or {})}

        if user_input is not None:
            try:
                await _validate_api(self.hass, data)
                return self.async_create_entry(title="", data=user_input)
            except ValueError as e:
                errors["base"] = "auth" if str(e) == "auth" else "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        d = self.config_entry.data
        schema = vol.Schema({
            vol.Optional(CONF_POINT, default=d.get(CONF_POINT, DEFAULTS[CONF_POINT])): int,
            vol.Optional(CONF_TYPE, default=d.get(CONF_TYPE, DEFAULTS[CONF_TYPE])): int,
            vol.Optional(CONF_ACTIVITY, default=d.get(CONF_ACTIVITY, DEFAULTS[CONF_ACTIVITY])): int,
            vol.Optional(CONF_CLASSIFICATION, default=d.get(CONF_CLASSIFICATION, DEFAULTS[CONF_CLASSIFICATION])): vol.In([1, 2, 3]),
            vol.Optional(CONF_GRANULARITY, default=d.get(CONF_GRANULARITY, DEFAULTS[CONF_GRANULARITY])): vol.In([4, 5, 6]),
            vol.Optional(CONF_GRAN_TZ, default=d.get(CONF_GRAN_TZ, DEFAULTS[CONF_GRAN_TZ])): int,
            vol.Optional(CONF_LOOKAHEAD_HOURS, default=d.get(CONF_LOOKAHEAD_HOURS, DEFAULTS[CONF_LOOKAHEAD_HOURS])): vol.All(int, vol.Range(min=1, max=168)),
            vol.Optional(CONF_UPDATE_INTERVAL_MIN, default=d.get(CONF_UPDATE_INTERVAL_MIN, DEFAULTS[CONF_UPDATE_INTERVAL_MIN])): vol.All(int, vol.Range(min=5, max=1440)),
            vol.Optional(CONF_UNIT, default=d.get(CONF_UNIT, DEFAULTS[CONF_UNIT])): vol.In(["g_per_kwh", "kg_per_kwh"]),
        })
        return self.async_show_form(step_id="edit", data_schema=schema, errors=errors)

@callback
def async_get_options_flow(config_entry):
    return NedCo2OptionsFlowHandler(config_entry)
