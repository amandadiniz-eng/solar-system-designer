# Solar System Designer

A tool that sizes a residential on-grid photovoltaic (PV) system -- recommended system size (kWp), number of panels, matching inverter, and estimated monthly generation -- from location, monthly energy consumption, available roof area, and shading level.

## Scope (V1)

This project sizes a residential on-grid PV system (kWp, number of modules, inverter, and estimated generation) from city, monthly consumption, available area, and shading level, using peak sun hours (HSP) and a performance ratio (PR) loss factor.

## Why this project

I'm an electrical engineer with 7+ years in power distribution and generation, currently building a stronger software/data skill set. This project applies core PV engineering fundamentals (solar irradiance, tilt angle, performance ratio, inverter sizing) inside a small, testable Python tool -- the kind of quantitative, automatable thinking the energy sector increasingly relies on.

## Inputs (V1)

- City / State (used to look up latitude and average peak sun hours)
- Monthly energy consumption (kWh)
- Available roof area (m2)
- Shading level: none / light / medium / heavy
- Target compensation (%): how much of consumption the system should offset

## Automatically calculated

- Latitude (via city lookup)
- Ideal orientation (North in the Southern Hemisphere, South in the Northern Hemisphere)
- Suggested tilt angle (~= |latitude|), the standard rule of thumb for fixed annual PV tilt

## Outputs (V1)

- Recommended system size (kWp)
- Number of modules and selected module model (from a 12-model catalog)
- Occupied roof area (m2)
- Selected inverter model and its DC/AC ratio (from a 10-model catalog)
- Estimated generation (kWh/month)

## Method

Daily energy target:

```
E_day = (monthly_consumption x target_compensation) / 30
```

Required system size:

```
kWp = E_day / (HSP x PR x orientation_factor x shading_factor)
```

Module selection: the catalog module with the highest kWp per m2 is chosen, to make the best use of limited roof area.

Number of modules:

```
n = ceil((kWp x 1000) / module_power_w)
```

Occupied area:

```
A = n x module_area_m2   # validated against available area
```

Inverter selection: the smallest string inverter whose rated AC power, multiplied by a standard DC/AC oversizing allowance (1.3x), still covers the array's kWp. Microinverters are cataloged separately and not yet auto-selected in V1 (see roadmap).

Default loss factors:

| Factor | Value |
|---|---|
| Performance ratio (PR) | 0.80 |
| Orientation (ideal / not ideal) | 1.00 / 0.95 |
| Shading: none | 1.00 |
| Shading: light | 0.92 |
| Shading: medium | 0.85 |
| Shading: heavy | 0.70 |

## Data

- `data/modules.csv` -- 12 residential PV modules (350W-500W) from Qcells, Panasonic, REC Group, Canadian Solar, JinkoSolar, Trina Solar, SunPower/Maxeon, and LONGi Solar, based on manufacturer datasheets.
- `data/inverters.csv` -- 10 residential inverters (string and microinverter) from Enphase, SolarEdge, Fronius, SMA, Growatt, and GoodWe.
- `data/hsp.csv` -- latitude and average peak sun hours for 5 Brazilian cities.

## Example

```python
from src.sizing import size_system

result = size_system(
    city="Rio de Janeiro",
    monthly_consumption_kwh=350,
    available_area_m2=30,
    shading="light",
    target_compensation=0.95,
)
```

```
city: Rio de Janeiro
latitude: -22.9
recommended_tilt_deg: 22.9
recommended_kwp: 3.14
module: Hi-MO X10 Explorer
n_modules: 7
occupied_area_m2: 14.28
fits_available_area: True
inverter: SE3800H-US
inverter_power_kw: 3.8
dc_ac_ratio: 0.83
estimated_generation_kwh_month: 361.4
```

## Roadmap (V2+)

- Battery / hybrid system sizing
- Microinverter-based system option (per-panel selection)
- Temperature-corrected power output
- Single-line diagram generation
- Support for more cities and a real geocoding lookup

## Status

Work in progress -- V1 core sizing logic implemented and validated, including module and inverter selection.
