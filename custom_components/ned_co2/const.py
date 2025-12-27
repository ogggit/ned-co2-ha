
from __future__ import annotations

# Domeinnaam van de integratie (moet gelijk zijn aan de mapnaam under custom_components/)
DOMAIN = "ned_co2"

# Config keys (gebruikt in config_flow, options en coordinator)
CONF_API_KEY = "api_key"
CONF_POINT = "point_id"
CONF_TYPE = "type_id"
CONF_ACTIVITY = "activity_id"
CONF_CLASSIFICATION = "classification_id"
CONF_GRANULARITY = "granularity_id"
CONF_GRAN_TZ = "granularity_timezone_id"
CONF_LOOKAHEAD_HOURS = "lookahead_hours"
CONF_UPDATE_INTERVAL_MIN = "update_interval_minutes"
CONF_UNIT = "unit"  # "g_per_kwh" of "kg_per_kwh"

# Standaardwaarden die in de UI als defaults worden getoond
DEFAULTS = {
    CONF_POINT: 0,                 # 0 = Nederland totaal
    CONF_TYPE: 27,                 # Elektriciteitsmix
    CONF_ACTIVITY: 1,              # CO₂-emissiefactor
    CONF_CLASSIFICATION: 1,        # 1=forecast, 2=actueel, 3=backcast
    CONF_GRANULARITY: 5,           # 4=15 min, 5=uur, 6=dag
    CONF_GRAN_TZ: 1,               # 1=CET
    CONF_LOOKAHEAD_HOURS: 24,      # venster (uren)
    CONF_UPDATE_INTERVAL_MIN: 30,  # update-interval (minuten)
    CONF_UNIT: "g_per_kwh",        # weergave-eenheid in sensoren
}
