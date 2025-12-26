## Purpose
Short instructions to help AI coding agents work productively on this Home Assistant custom integration.

## Big picture
- This is a Home Assistant custom integration providing CO₂ intensity sensors using the NED API. Key code lives in `custom_components/ned_co2`.
- `custom_components/ned_co2/__init__.py` sets up the integration and creates a `NedCo2Coordinator` stored in `hass.data[DOMAIN][entry_id]`.
- `coordinator.py` implements a `DataUpdateCoordinator` that calls `https://api.ned.nl/v1/utilizations` and returns a `series`, `current`, and `min_item` payload consumed by entities.
- `sensor.py` implements two `CoordinatorEntity` sensors (`current` and `min`) and exposes `points` in `extra_state_attributes` for charts.

## Important patterns & conventions
- Coordinator pattern: use `DataUpdateCoordinator` (_see_ `coordinator.py`) and `CoordinatorEntity` in `sensor.py`.
- Config values and defaults are centralized in `const.py` (`CONF_*` keys and `DEFAULTS`). Merge `entry.data` with `DEFAULTS` when reading config.
- API auth: header `X-AUTH-TOKEN`. Validation logic is in `config_flow.py` (`_validate_api`) and mirrors coordinator requests.
- Retry & error handling: coordinator raises `UpdateFailed` for HTTP errors; 429 handling does a single retry after a short sleep.
- Units: integration supports `g_per_kwh` and `kg_per_kwh`; conversion logic lives in `sensor.py` and coordinator returns `emissionfactor_kg_per_kwh`.
- Entity unique IDs: config flow calls `async_set_unique_id(f"ned_co2_{point}")`. Sensor unique IDs are `{entry_id}_current` and `{entry_id}_min`.

## Developer workflows
- Install locally by copying `custom_components/ned_co2` to Home Assistant `config/custom_components/` and restart HA (standard HA dev flow).
- Logging: use logger `custom_components.ned_co2`. To debug, enable that logger in Home Assistant's `configuration.yaml` (or via UI).
- Validate API connectivity by calling the same endpoint and params used in `_validate_api`/`_build_params` (see `config_flow.py` and `coordinator.py`).

## Files to inspect for common edits
- Integration setup: [custom_components/ned_co2/__init__.py](custom_components/ned_co2/__init__.py)
- Coordinator & API logic: [custom_components/ned_co2/coordinator.py](custom_components/ned_co2/coordinator.py)
- Entities & state shaping: [custom_components/ned_co2/sensor.py](custom_components/ned_co2/sensor.py)
- Config flow & validation: [custom_components/ned_co2/config_flow.py](custom_components/ned_co2/config_flow.py)
- Constants/defaults: [custom_components/ned_co2/const.py](custom_components/ned_co2/const.py)
- Manifest & metadata: [custom_components/ned_co2/manifest.json](custom_components/ned_co2/manifest.json)

## Examples / snippets agents should follow
- Build request params (from `coordinator.py`): use UTC ISO timestamps (`validfrom[after]`, `validfrom[strictly_before]`) and integer casts for config keys.
- Handling API responses: expect either a list or a Hydra-wrapped object (`hydra:member`) and map items to `emissionfactor_kg_per_kwh` and derived `emissionfactor_g_per_kwh`.
- Time handling: use `homeassistant.util.dt` helpers (`utcnow`, `parse_datetime`) and convert to local timezone for `extra_state_attributes`.

## What NOT to change without verification
- The shape of the coordinator return value (`series`, `current`, `min_item`, `meta`) — entities and dashboards rely on these keys.
- `DEFAULTS` keys and meaning in `const.py`; changing numeric IDs (point/type/activity) can break existing installs.

## Quick tasks an agent can do confidently
- Update or extend `extra_state_attributes` in `sensor.py` (keep `points` array shape).
- Add more robust 429/rate-limit backoff in `coordinator.py` (ensure tests or manual validation against API).
- Add unit tests that simulate `session.get` responses for `coordinator._async_update_data`.

## References
- Readme: [README.md](README.md)

---
If anything above is unclear or you want more detail for automated tests, tell me which area to expand.  