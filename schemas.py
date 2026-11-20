"""Response models. They define the Swagger schemas at /docs."""
from datetime import date as date_type
from typing import Any

from pydantic import BaseModel, Field

Number = int | float

WEEKLY = "One value per week, aligned with /index. Weeks without runs are 0."


class DistanceWeeks(BaseModel):
    distance: list[Number] = Field(description=f"Distance in meters. {WEEKLY}")
    elevationGain: list[Number] = Field(description=f"Elevation gain in meters. {WEEKLY}")
    elevationLoss: list[Number] = Field(description=f"Elevation loss in meters. {WEEKLY}")
    kilometerEffort: list[Number] = Field(description=f"Distance + 10 × elevation gain, in meters. {WEEKLY}")
    fullKilometerEffort: list[Number] = Field(
        description=f"Distance + 10 × elevation gain + 3 × elevation loss, in meters. {WEEKLY}")


def _zone(kind: str, zone: int):
    return Field(description=f"Seconds in {kind} zone {zone}. {WEEKLY}")


class HrTimeInZoneWeeks(BaseModel):
    hrTimeInZone_1: list[Number] = _zone("heart rate", 1)
    hrTimeInZone_2: list[Number] = _zone("heart rate", 2)
    hrTimeInZone_3: list[Number] = _zone("heart rate", 3)
    hrTimeInZone_4: list[Number] = _zone("heart rate", 4)
    hrTimeInZone_5: list[Number] = _zone("heart rate", 5)


class PowerTimeInZoneWeeks(BaseModel):
    powerTimeInZone_1: list[Number] = _zone("power", 1)
    powerTimeInZone_2: list[Number] = _zone("power", 2)
    powerTimeInZone_3: list[Number] = _zone("power", 3)
    powerTimeInZone_4: list[Number] = _zone("power", 4)
    powerTimeInZone_5: list[Number] = _zone("power", 5)


WeeklyMetrics = dict[str, list[Number | None]]
ActivityMetrics = dict[str, list[Any]]


TSS = ("hrTSS: Banister TRIMP from duration and averageHR, scaled so 1 hour at LTHR = 100. "
       "Thresholds come from the thresholds collection, by date.")
LOAD = ("CTL and ATL are exponential averages of daily TSS over 42 and 7 days. TSB = previous day's CTL - ATL. "
        "Computed from the first run in history, so the first ~6 weeks of history underestimate CTL.")


class TrainingLoadWeeks(BaseModel):
    tss: list[Number | None] = Field(description=f"Sum of the week's hrTSS. {TSS} {WEEKLY}")
    ctl: list[Number | None] = Field(description=f"Fitness on the week's last day (up to today). {LOAD}")
    atl: list[Number | None] = Field(description=f"Fatigue on the week's last day (up to today). {LOAD}")
    tsb: list[Number | None] = Field(description=f"Form on the week's last day (up to today). {LOAD}")


class TrainingLoadDays(BaseModel):
    date: list[date_type] = Field(description="Every day from the Monday of the first week to the last day of the range, up to today.")
    tss: list[Number] = Field(description=f"Sum of the day's hrTSS. {TSS}")
    ctl: list[Number] = Field(description=f"Fitness. {LOAD}")
    atl: list[Number] = Field(description=f"Fatigue. {LOAD}")
    tsb: list[Number] = Field(description=f"Form. {LOAD}")


class WeekType(BaseModel):
    date: str = Field(description="Monday of the week, YYYY-MM-DD.", examples=["2025-11-10"])
    label: str = Field(examples=["Récupération"])


class ErrorDetail(BaseModel):
    detail: str
