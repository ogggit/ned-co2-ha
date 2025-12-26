from __future__ import annotations

DOMAIN = "ned_co2"

CONF_API_KEY = "api_key"
CONF_POINT = "point_id"
CONF_TYPE = "type_id"
CONF_ACTIVITY = "activity_id"
CONF_CLASSIFICATION = "classification_id"
CONF_GRANULARITY = "granularity_id"
CONF_GRAN_TZ = "granularity_timezone_id"
CONF_LOOKAHEAD_HOURS = "lookahead_hours"
CONF_UPDATE_INTERVAL_MIN = "update_interval_minutes"
CONF_UNIT = "unit"  # "g_per_kwh" or "kg_per_kwh"

DEFAULTS = {
    CONF_POINT: 0,
    CONF_TYPE: 27,
    CONF_ACTIVITY: 1,
    CONF_CLASSIFICATION: 1,
    CONF_GRANULARITY: 5,
    CONF_GRAN_TZ: 1,
    CONF_LOOKAHEAD_HOURS: 24,
    CONF_UPDATE_INTERVAL_MIN: 30,
    CONF_UNIT: "g_per_kwh",
}
