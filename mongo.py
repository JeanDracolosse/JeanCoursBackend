from pymongo import MongoClient, ASCENDING
from pymongo.server_api import ServerApi
from pymongo.database import Database
from pymongo.collection import Collection

import os
from dotenv import load_dotenv
from datetime import date, datetime, time, timedelta

from aggregation import (DISTANCE_FIELDS, HR_TIME_IN_ZONE_FIELDS, POWER_TIME_IN_ZONE_FIELDS, RUNNING_TYPES, ActivityFilter,
                         date_range_pipeline, get_metric_list_pipeline_by_activity, get_week_types_pipeline, week_monday,
                         activity_match, weighted_average_fields, weekly_pipeline)
from training_load import Threshold, daily_load, hr_tss, threshold_on

load_dotenv()


def __get_database() -> Database:
    uri = f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_URL')}/?retryWrites=true&w=majority&appName={os.getenv('MONGO_APP_NAME')}"
    client = MongoClient(uri, server_api=ServerApi('1'))
    return client.jeanCours


database = __get_database()


def __get_or_create_collection(collection_name: str, index_list: list[str] = []) -> Collection:
    collection = database.get_collection(collection_name)
    if collection.count_documents({}) == 0:
        for index in index_list:
            collection .create_index([(index, ASCENDING)],  unique=True)
    return collection


activities_collection = __get_or_create_collection(
    "activities", ["activityId"])
configuration_collection = __get_or_create_collection("configuration")
week_type_collection = __get_or_create_collection("weekTypes", ["weekTypeId"])
week_collection = __get_or_create_collection("weeks", ["date"])
threshold_collection = __get_or_create_collection("thresholds", ["date"])


class NoThresholds(Exception):
    """Training load needs at least one threshold in the thresholds collection."""


def upsert_activity(activity: dict) -> None:
    activities_collection.update_one({"activityId": activity['activityId']}, {
                                     "$set": activity}, upsert=True)
    
def upsert_week_type(week_type: dict) -> None:
    week_type_collection.update_one({"weekTypeId": week_type['weekTypeId']}, {
                                     "$set": week_type}, upsert=True)   

def upsert_week(week: dict) -> None:
    week_collection.update_one({"date": week['date']}, {
                                     "$set": week}, upsert=True)


def upsert_threshold(threshold: dict) -> None:
    threshold_collection.update_one({"date": threshold["date"]}, {"$set": threshold}, upsert=True)


def get_thresholds() -> list[Threshold]:
    return [
        Threshold(date.fromisoformat(doc["date"]), doc["lthr"], doc["restingHr"], doc["maxHr"], doc["trimpA"], doc["trimpB"])
        for doc in threshold_collection.find().sort("date", ASCENDING)
    ]

# Data operations


def get_last_date() -> date:
    configuration = configuration_collection.find_one()

    if configuration is None:
        last_date = datetime.today().date()
    else:
        last_date = date.fromisoformat(configuration['lastDate'])

    return last_date


def set_last_date() -> None:
    configuration_collection.update_many(
        {}, {"$set": {'lastDate': datetime.today().date().isoformat()}}, upsert=True)

# Aggregations


def get_indexes(activity_filter: ActivityFilter = ActivityFilter()) -> list[datetime]:
    """Returns the Monday of every week in the range, including weeks without runs."""
    return [datetime.combine(monday, time.min) for monday in __weeks(activity_filter)]


def get_hr_time_in_zone(activity_filter: ActivityFilter = ActivityFilter()) -> dict:
    return __weekly_arrays(activity_filter, HR_TIME_IN_ZONE_FIELDS)


def get_power_time_in_zone(activity_filter: ActivityFilter = ActivityFilter()) -> dict:
    return __weekly_arrays(activity_filter, POWER_TIME_IN_ZONE_FIELDS)


def get_distance(activity_filter: ActivityFilter = ActivityFilter()) -> dict:
    return __weekly_arrays(activity_filter, DISTANCE_FIELDS)


def get_cumulative_metric_list_by_week(metric_list: list, activity_filter: ActivityFilter = ActivityFilter()) -> dict:
    return __weekly_arrays(activity_filter, {metric: 1 for metric in metric_list})


def get_average_metric_list_by_week(metric_list: list, activity_filter: ActivityFilter = ActivityFilter()) -> dict:
    """Averages each metric per week, weighted by run duration. None when no run has it."""
    sums = __weekly_arrays(activity_filter, weighted_average_fields(metric_list))
    return {
        metric: [weighted / duration if duration else None
                 for weighted, duration in zip(sums[f"{metric}__weighted"], sums[f"{metric}__duration"])]
        for metric in metric_list
    }


def get_metric_list_by_activity(year: int, week: int, metric_list: list, types: tuple[int, ...] = RUNNING_TYPES) -> dict:
    metrics = list(metric_list)
    if "startTimeLocal" not in metrics:
        metrics.append("startTimeLocal")
    results = list(activities_collection.aggregate(get_metric_list_pipeline_by_activity(year, week, metrics, types)))
    if not results:
        return {metric: [] for metric in metrics}
    results[0].pop("_id")
    return results[0]


def get_training_load_by_day(activity_filter: ActivityFilter = ActivityFilter()) -> dict[str, list]:
    """Returns daily TSS, CTL, ATL and TSB over the weeks of the range, up to today.

    CTL and ATL start from the first matching run in all history, so they are warmed up
    even when the range starts later.

    Raises:
        NoThresholds: No threshold is stored.
    """
    thresholds = get_thresholds()
    if not thresholds:
        raise NoThresholds("No heart-rate threshold stored. Run setThresholds.py first.")
    mondays = __weeks(activity_filter)
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
    for monday in __weeks(activity_filter):
        days = [day_index[monday + timedelta(days=offset)] for offset in range(7)
                if monday + timedelta(days=offset) in day_index]
        weekly["tss"].append(sum(daily["tss"][index] for index in days) if days else None)
        for key in ("ctl", "atl", "tsb"):
            weekly[key].append(daily[key][days[-1]] if days else None)
    return weekly


def __weeks(activity_filter: ActivityFilter) -> list[date]:
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


def __weekly_arrays(activity_filter: ActivityFilter, fields: dict, accumulator: str = "$sum", empty=0) -> dict:
    """Returns one array per field, one value per week in the range.

    Weeks without runs get `empty`.
    """
    pipeline = weekly_pipeline(activity_filter, fields, accumulator)
    by_week = {(doc["_id"]["year"], doc["_id"]["week"]): doc for doc in activities_collection.aggregate(pipeline)}
    weeks = [tuple(monday.isocalendar())[:2] for monday in __weeks(activity_filter)]
    return {field: [by_week[week].get(field, empty) if week in by_week else empty for week in weeks] for field in fields}

def get_week_types() -> dict:
    cursor = week_collection.aggregate(get_week_types_pipeline())
    return [data for data in cursor]
