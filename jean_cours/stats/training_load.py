"""Heart-rate training load: hrTSS (Banister TRIMP), CTL, ATL and TSB."""
import math
from dataclasses import dataclass
from datetime import date, timedelta

CTL_DAYS = 42
ATL_DAYS = 7


@dataclass(frozen=True)
class Threshold:
    """Heart-rate thresholds in effect from `date`."""
    date: date
    lthr: float
    resting_hr: float
    max_hr: float
    trimp_a: float
    trimp_b: float


def threshold_on(day: date, thresholds: list[Threshold]) -> Threshold:
    """Returns the latest threshold dated on or before `day`.

    Days before the first threshold use the first one. `thresholds` must be sorted by date.
    """
    current = thresholds[0]
    for threshold in thresholds:
        if threshold.date > day:
            break
        current = threshold
    return current


def _trimp(minutes: float, heart_rate: float, threshold: Threshold) -> float:
    reserve = (heart_rate - threshold.resting_hr) / (threshold.max_hr - threshold.resting_hr)
    reserve = min(max(reserve, 0.0), 1.0)
    return minutes * reserve * threshold.trimp_a * math.exp(threshold.trimp_b * reserve)


def hr_tss(duration_s: float | None, average_hr: float | None, threshold: Threshold) -> float:
    """Returns the TRIMP of a run, scaled so 1 hour at LTHR is 100. 0 without HR or duration."""
    if not duration_s or not average_hr:
        return 0.0
    return _trimp(duration_s / 60, average_hr, threshold) / _trimp(60, threshold.lthr, threshold) * 100


def daily_load(tss_by_day: dict[date, float], first_day: date, last_day: date) -> dict[str, list]:
    """Computes TSS, CTL, ATL and TSB for each day, starting from 0 on `first_day`.

    TSB is the previous day's CTL - ATL, so it reflects form before the day's training.
    """
    ctl = atl = 0.0
    load = {"date": [], "tss": [], "ctl": [], "atl": [], "tsb": []}
    day = first_day
    while day <= last_day:
        tss = tss_by_day.get(day, 0.0)
        tsb = ctl - atl
        ctl += (tss - ctl) / CTL_DAYS
        atl += (tss - atl) / ATL_DAYS
        for key, value in (("date", day), ("tss", tss), ("ctl", ctl), ("atl", atl), ("tsb", tsb)):
            load[key].append(value)
        day += timedelta(days=1)
    return load
