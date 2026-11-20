"""Stats queries over the activities. Weekly results are parallel arrays aligned with get_indexes."""
from datetime import date, datetime, time, timedelta

from pymongo import ASCENDING

from jean_cours.db import activities_collection, threshold_collection, week_collection
from jean_cours.stats.pipelines import (DISTANCE_FIELDS, HR_TIME_IN_ZONE_FIELDS, POWER_TIME_IN_ZONE_FIELDS,
                                        RUNNING_TYPES, ActivityFilter, activity_match, date_range_pipeline,
                                        get_metric_list_pipeline_by_activity, get_week_types_pipeline,
                                        weekly_pipeline, week_monday, weighted_average_fields)
from jean_cours.stats.training_load import Threshold, daily_load, hr_tss, threshold_on


class NoThresholds(Exception):
    """Training load needs at least one threshold in the thresholds collection."""


def get_indexes(activity_filter: ActivityFilter = ActivityFilter()) -> list[datetime]:
    """Returns the Monday of every week in the range, including weeks without runs."""
    return [datetime.combine(monday, time.min) for monday in _weeks(activity_filter)]


def get_hr_time_in_zone(activity_filter: ActivityFilter = ActivityFilter()) -> dict[str, list]:
    return _weekly_arrays(activity_filter, HR_TIME_IN_ZONE_FIELDS)


def get_power_time_in_zone(activity_filter: ActivityFilter = ActivityFilter()) -> dict[str, list]:
    return _weekly_arrays(activity_filter, POWER_TIME_IN_ZONE_FIELDS)


def get_distance(activity_filter: ActivityFilter = ActivityFilter()) -> dict[str, list]:
    return _weekly_arrays(activity_filter, DISTANCE_FIELDS)


def get_cumulative_metric_list_by_week(metric_list: list[str],
                                       activity_filter: ActivityFilter = ActivityFilter()) -> dict[str, list]:
    return _weekly_arrays(activity_filter, {metric: 1 for metric in metric_list})


def get_average_metric_list_by_week(metric_list: list[str],
                                    activity_filter: ActivityFilter = ActivityFilter()) -> dict[str, list]:
    """Averages each metric per week, weighted by run duration. None when no run has it."""
    sums = _weekly_arrays(activity_filter, weighted_average_fields(metric_list))
    return {
        metric: [weighted / duration if duration else None
                 for weighted, duration in zip(sums[f"{metric}__weighted"], sums[f"{metric}__duration"])]
        for metric in metric_list
    }


def get_metric_list_by_activity(year: int, week: int, metric_list: list[str],
                                types: tuple[int, ...] = RUNNING_TYPES) -> dict[str, list]:
    metrics = list(metric_list)
    if "startTimeLocal" not in metrics:
        metrics.append("startTimeLocal")
    results = list(activities_collection.aggregate(get_metric_list_pipeline_by_activity(year, week, metrics, types)))
    if not results:
        return {metric: [] for metric in metrics}
    results[0].pop("_id")
    return results[0]


def get_week_types() -> list[dict]:
    return list(week_collection.aggregate(get_week_types_pipeline()))


def get_thresholds() -> list[Threshold]:
    return [
        Threshold(date.fromisoformat(doc["date"]), doc["lthr"], doc["restingHr"], doc["maxHr"], doc["trimpA"], doc["trimpB"])
        for doc in threshold_collection.find().sort("date", ASCENDING)
    ]


def get_training_load_by_day(activity_filter: ActivityFilter = ActivityFilter()) -> dict[str, list]:
    """Returns daily TSS, CTL, ATL and TSB over the weeks of the range, up to today.

    CTL and ATL start from the first matching run in all history, so they are warmed up
    even when the range starts later.

    Raises:
        NoThresholds: No threshold is stored.
    """
    thresholds = get_thresholds()
    if not thresholds:
        raise NoThresholds("No heart-rate threshold stored. Run scripts/set_thresholds.py first.")
    mondays = _weeks(activity_filter)
    if not mondays:
        return {"date": [], "tss": [], "ctl": [], "atl": [], "tsb": []}

    last_day = mondays[-1] + timedelta(days=6)
    if mondays[0] <= date.today() < last_day:
        last_day = date.today()

    tss_by_day = {}
    runs = activities_collection.find(activity_match(ActivityFilter(types=activity_filter.types)),
                                      {"startTimeLocal": 1, "duration": 1, "averageHR": 1})
    for run in runs:
        day = run["startTimeLocal"].date()
        tss = hr_tss(run.get("duration"), run.get("averageHR"), threshold_on(day, thresholds))
        tss_by_day[day] = tss_by_day.get(day, 0.0) + tss

    first_day = min([mondays[0], *tss_by_day])
    load = daily_load(tss_by_day, first_day, last_day)
    start = load["date"].index(mondays[0])
    return {key: values[start:] for key, values in load.items()}


def get_training_load(activity_filter: ActivityFilter = ActivityFilter()) -> dict[str, list]:
    """Returns weekly TSS (sum) and CTL, ATL, TSB (on the week's last day), aligned with get_indexes.

    Raises:
        NoThresholds: No threshold is stored.
    """
    daily = get_training_load_by_day(activity_filter)
    day_index = {day: index for index, day in enumerate(daily["date"])}
    weekly = {"tss": [], "ctl": [], "atl": [], "tsb": []}
    for monday in _weeks(activity_filter):
        days = [day_index[day] for day in (monday + timedelta(days=offset) for offset in range(7)) if day in day_index]
        weekly["tss"].append(sum(daily["tss"][index] for index in days) if days else None)
        for key in ("ctl", "atl", "tsb"):
            weekly[key].append(daily[key][days[-1]] if days else None)
    return weekly


def _weeks(activity_filter: ActivityFilter) -> list[date]:
    """Lists the Monday of every week in the range.

    A missing bound is taken from the first or last matching run.
    """
    start, end = activity_filter.start, activity_filter.end
    if start is None or end is None:
        runs = list(activities_collection.aggregate(date_range_pipeline(activity_filter)))
        if runs:
            start = start or runs[0]["first"].date()
            end = end or runs[0]["last"].date()
        start, end = start or end, end or start
    if start is None:
        return []

    mondays = []
    monday = week_monday(start)
    while monday <= end:
        mondays.append(monday)
        monday += timedelta(days=7)
    return mondays


def _weekly_arrays(activity_filter: ActivityFilter, fields: dict, accumulator: str = "$sum", empty=0) -> dict[str, list]:
    """Returns one array per field, one value per week in the range.

    Weeks without runs get `empty`.
    """
    pipeline = weekly_pipeline(activity_filter, fields, accumulator)
    by_week = {(doc["_id"]["year"], doc["_id"]["week"]): doc for doc in activities_collection.aggregate(pipeline)}
    weeks = [tuple(monday.isocalendar())[:2] for monday in _weeks(activity_filter)]
    return {field: [by_week[week].get(field, empty) if week in by_week else empty for week in weeks] for field in fields}
