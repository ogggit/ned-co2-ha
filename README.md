# NED CO₂ intensiteit (Home Assistant custom integration)

This software is vibecoded and provided as is. Below more information in Dutch. 

Deze integratie haalt de **CO₂‑emissiefactor van de Nederlandse elektriciteitsmix** op uit het Nationaal Energie Dashboard (**NED**) en presenteert die in Home Assistant als sensoren. De emissiefactor wordt door de NED‑API geleverd als **kg/kWh** en wordt in de sensor (standaard) omgerekend naar **g/kWh**.

- API‑endpoint: `/v1/utilizations` (parameters: `point`, `type`, `activity`, `classification`, `granularity`, `granularitytimezone`, `validfrom[...]`)
- Authenticatie: header **`X-AUTH-TOKEN: <API_KEY>`**

> Referenties:
> - Voorbeeldrequest met `emissionfactor` (kg/kWh) en header `X-AUTH-TOKEN` \[GitHub issue/voorbeeld\].
> - API resources index (`/v1`) toont o.a. `Utilization`, `Point`, `Granularity`, `Classification`.
> - Community tooling en Python client tonen de parameters en limieten.

## Installatie
1. Kopieer de map `custom_components/ned_co2` naar je Home Assistant `config/` map.
2. Herstart Home Assistant.
3. Voeg de integratie toe via **Instellingen → Apparaten & Diensten → Integraties → +** en selecteer **NED CO₂ intensiteit**.
4. Vul je **API‑key** en parameters in (alles is ook later via **Opties** aan te passen).

## Sensoren
- `sensor.ned_co2_intensity_now`: huidige/volgende periode in g/kWh of kg/kWh (instelbaar), met attribuut `points` (reeks voor grafieken).
- `sensor.ned_co2_intensity_min_window`: minimum in het ingestelde venster (plus tijdstip).

## Opties
- **Point** (standaard 0 = NL totaal)
- **Type** (standaard 27 = elektriciteitsmix)
- **Activity** (standaard 1 = CO₂‑emissiefactor)
- **Classification** (1=forecast, 2=actueel, 3=backcast)
- **Granularity** (4=15m, 5=uur, 6=dag)
- **Granularity timezone** (1=CET)
- **Look‑ahead window** (uren; standaard 24)
- **Update interval** (minuten; standaard 30)
- **Eenheid** (g/kWh of kg/kWh)

## ApexCharts voorbeeld
```yaml
type: custom:apexcharts-card
header:
  show: true
  title: CO₂-intensiteit komende 24 uur
series:
  - entity: sensor.ned_co2_intensity_now
    name: g/kWh
    type: line
    data_generator: |
      const pts = entity.attributes.points || [];
      return pts.map(p => [new Date(p.t).getTime(), p.g_per_kwh]);
```

## Licentie
MIT © 2025
