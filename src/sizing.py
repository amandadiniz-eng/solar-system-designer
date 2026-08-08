"""
Solar System Designer - V1 core sizing logic.

Sizes a residential on-grid PV system (kWp, number of modules, inverter,
estimated generation) from city, monthly consumption, available roof area,
and shading level, using peak sun hours (HSP) and a performance ratio (PR)
loss factor.
"""
import csv
import math
from dataclasses import dataclass

SHADING_FACTORS = {
    "none": 1.00,
    "light": 0.92,
    "medium": 0.85,
    "heavy": 0.70,
}

DEFAULT_PR = 0.80
MAX_DC_AC_RATIO = 1.3  # standard oversizing allowance for string inverters


@dataclass
class Module:
    model: str
    manufacturer: str
    power_w: float
    area_m2: float
    price_usd: float

    @property
    def kwp_per_m2(self) -> float:
        return (self.power_w / 1000) / self.area_m2


@dataclass
class Inverter:
    model: str
    manufacturer: str
    type: str  # "string" or "microinverter"
    power_kw: float
    price_usd: float


def load_modules(path: str) -> list[Module]:
    modules = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            modules.append(
                Module(
                    model=row["model"],
                    manufacturer=row["manufacturer"],
                    power_w=float(row["power_w"]),
                    area_m2=float(row["area_m2"]),
                    price_usd=float(row["price_usd"]),
                )
            )
    return modules


def load_inverters(path: str) -> list[Inverter]:
    inverters = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            inverters.append(
                Inverter(
                    model=row["model"],
                    manufacturer=row["manufacturer"],
                    type=row["type"],
                    power_kw=float(row["power_kw"]),
                    price_usd=float(row["price_usd"]),
                )
            )
    return inverters


def load_hsp(path: str) -> dict:
    cities = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = row["city"].strip().lower()
            cities[key] = {
                "state": row["state"],
                "latitude": float(row["latitude"]),
                "hsp_avg": float(row["hsp_avg"]),
            }
    return cities


def recommended_tilt(latitude: float) -> float:
    """Best fixed annual tilt angle ~= |latitude| (standard practice)."""
    return abs(latitude)


def orientation_factor(is_ideal_orientation: bool) -> float:
    return 1.00 if is_ideal_orientation else 0.95


def required_kwp(
    monthly_consumption_kwh: float,
    target_compensation: float,
    hsp: float,
    shading: str,
    pr: float = DEFAULT_PR,
    ideal_orientation: bool = True,
) -> float:
    e_day = (monthly_consumption_kwh * target_compensation) / 30
    shading_factor = SHADING_FACTORS[shading]
    orient_factor = orientation_factor(ideal_orientation)
    return e_day / (hsp * pr * orient_factor * shading_factor)


def choose_module(modules: list[Module]) -> Module:
    """Pick the module with the highest kWp per m^2 (best use of limited roof area)."""
    return max(modules, key=lambda m: m.kwp_per_m2)


def choose_inverter(
    kwp: float, inverters: list[Inverter], max_dc_ac_ratio: float = MAX_DC_AC_RATIO
) -> Inverter:
    """Pick the smallest string inverter that can handle the array's DC power,
    allowing a standard DC/AC oversizing ratio. Falls back to the largest
    available string inverter if none is big enough (undersized case, V2 would
    split into multiple inverters/MPPTs)."""
    string_inverters = [i for i in inverters if i.type == "string"]
    candidates = [i for i in string_inverters if i.power_kw * max_dc_ac_ratio >= kwp]
    if candidates:
        return min(candidates, key=lambda i: i.power_kw)
    return max(string_inverters, key=lambda i: i.power_kw)


def size_system(
    city: str,
    monthly_consumption_kwh: float,
    available_area_m2: float,
    shading: str,
    target_compensation: float,
    modules_path: str = "data/modules.csv",
    inverters_path: str = "data/inverters.csv",
    hsp_path: str = "data/hsp.csv",
) -> dict:
    modules = load_modules(modules_path)
    inverters = load_inverters(inverters_path)
    cities = load_hsp(hsp_path)

    city_data = cities.get(city.strip().lower())
    if city_data is None:
        raise ValueError(f"City '{city}' not found in HSP database.")

    tilt = recommended_tilt(city_data["latitude"])
    kwp = required_kwp(
        monthly_consumption_kwh=monthly_consumption_kwh,
        target_compensation=target_compensation,
        hsp=city_data["hsp_avg"],
        shading=shading,
    )

    module = choose_module(modules)
    n_modules = math.ceil((kwp * 1000) / module.power_w)
    occupied_area = n_modules * module.area_m2
    fits = occupied_area <= available_area_m2

    inverter = choose_inverter(kwp, inverters)
    dc_ac_ratio = round(kwp / inverter.power_kw, 2)

    estimated_generation_kwh_month = kwp * city_data["hsp_avg"] * DEFAULT_PR * 30

    return {
        "city": city,
        "latitude": city_data["latitude"],
        "recommended_tilt_deg": round(tilt, 1),
        "recommended_kwp": round(kwp, 2),
        "module": module.model,
        "n_modules": n_modules,
        "occupied_area_m2": round(occupied_area, 2),
        "fits_available_area": fits,
        "inverter": inverter.model,
        "inverter_power_kw": inverter.power_kw,
        "dc_ac_ratio": dc_ac_ratio,
        "estimated_generation_kwh_month": round(estimated_generation_kwh_month, 1),
    }


if __name__ == "__main__":
    result = size_system(
        city="Rio de Janeiro",
        monthly_consumption_kwh=350,
        available_area_m2=30,
        shading="light",
        target_compensation=0.95,
    )
    for key, value in result.items():
        print(f"{key}: {value}")
