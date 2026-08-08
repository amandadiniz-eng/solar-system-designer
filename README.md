# Solar System Designer

A tool that sizes a residential on-grid photovoltaic (PV) system -- recommended system size (kWp), the lowest-cost module and inverter combination that fits the available roof area, and estimated monthly generation -- from location, monthly energy consumption, available roof area, and shading level.

## Scope (V1)

This project sizes a residential on-grid PV system (kWp, module and inverter selection, total equipment cost, and estimated generation) from city, monthly consumption, available area, and shading level, using peak sun hours (HSP) and a performance ratio (PR) loss factor.

## Why this project

I'm an electrical engineer with 7+ years in power distribution and generation, currently building a stronger software/data skill set. This project applies core PV engineering fundamentals (solar irradiance, tilt angle, performance ratio, inverter sizing, cost/benefit equipment selection) inside a small, testable Python tool -- the kind of quantitative, automatable thinking the energy sector increasingly relies on.

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
- Selected module model, number of modules, and occupied roof area (m2)
- Selected inverter model and its DC/AC ratio
- Modules cost, inverter cost, and total equipment cost (USD)
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

Module and layout selection: every module in the catalog is evaluated against the required kWp and the available roof area (number of modules needed, occupied area, total module cost). Among the combinations that fit the roof, the cheapest one is selected -- the best cost/benefit option for the client, not just the most area-efficient one. If nothing fits, the tool falls back to the most area-efficient module.

```
n = ceil((kWp x 1000) / module_power_w)
area = n x module_area_m2       # must be <= available area to "fit"
cost = n x module_price_usd
```

Inverter selection: among all string inverters whose rated AC power, multiplied by a standard DC/AC oversizing allowance (1.3x), still covers the array's kWp, the cheapest one is selected. Microinverters are cataloged separately and not yet auto-selected in V1 (see roadmap).

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

- `data/modules.csv` -- 42 residential PV modules spanning full datasheet power ranges (not just one model per brand) from Qcells, Panasonic, REC Group, Canadian Solar, JinkoSolar, Trina Solar, SunPower/Maxeon, and LONGi Solar.
- `data/inverters.csv` -- 41 residential inverters spanning full product lines (string and microinverter) from Enphase (IQ8 series), SolarEdge (Home Wave), Fronius (Primo GEN24), SMA (Sunny Boy), Growatt (MIN TL-X), and GoodWe (DNS/MS series).
- `data/hsp.csv` -- latitude and average peak sun hours for 5 Brazilian cities.

Module and inverter power ratings and model names come from manufacturer datasheets. Dimensions/areas and prices for the additional power variants within each product line are estimated from the confirmed reference model in that line (a manufacturer's datasheet usually shows one physical panel size sold in several power bins) and should be treated as reasonable engineering estimates rather than exact retail quotes. The LONGi Hi-MO 6 line's exact power steps could not be confirmed from an accessible datasheet and should be re-verified before using this catalog for a real quote.

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
module: Hi-MO 6 Explorer LR5-54HTH-415
n_modules: 8
occupied_area_m2: 16.0
fits_available_area: True
inverter: GW3000D-NS
inverter_power_kw: 3.0
dc_ac_ratio: 1.05
modules_cost_usd: 992
inverter_cost_usd: 510.0
total_system_cost_usd: 1502
estimated_generation_kwh_month: 361.4
```

## Roadmap (V2+)

- Battery / hybrid system sizing
- Microinverter-based system option (per-panel selection)
- Temperature-corrected power output
- Single-line diagram generation
- Support for more cities and a real geocoding lookup
- Replace estimated prices/areas for catalog line variants with confirmed per-SKU datasheet values

## Status

Work in progress -- V1 core sizing logic implemented and validated, including cost-driven module and inverter selection across full product lines.
