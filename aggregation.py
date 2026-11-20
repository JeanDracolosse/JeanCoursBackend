from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

RUNNING_TYPES = (1, 6)

# Shared by all weekly pipelines.
WEEK_GROUP_ID = {"year": "$year", "week": "$week"}

DISTANCE_FIELDS = {
    "distance": 1,
    "elevationGain": 1,
    "elevationLoss": 1,
    "kilometerEffort": {"$add": ["$distance", {"$multiply": ["$elevationGain", 10]}]},
    "fullKilometerEffort": {"$add": [
        "$distance",
        {"$multiply": ["$elevationGain", 10]},
        {"$multiply": ["$elevationLoss", 3]},
    ]},
}
HR_TIME_IN_ZONE_FIELDS = {f"hrTimeInZone_{zone}": 1 for zone in range(1, 6)}
POWER_TIME_IN_ZONE_FIELDS = {f"powerTimeInZone_{zone}": 1 for zone in range(1, 6)}


@dataclass(frozen=True)
class ActivityFilter:
    """Which activities the stats cover. A missing bound means no limit."""
    start: date | None = None
    end: date | None = None
    types: tuple[int, ...] = RUNNING_TYPES


def week_monday(day: date) -> date:
    return day - timedelta(days=day.weekday())


def activity_match(activity_filter: ActivityFilter) -> dict:
    """Builds the $match stage. Bounds are widened to whole weeks."""
    match = {"activityType.typeId": {"$in": list(activity_filter.types)}}
    bounds = {}
    if activity_filter.start:
        bounds["$gte"] = datetime.combine(week_monday(activity_filter.start), time.min)
    if activity_filter.end:
        bounds["$lt"] = datetime.combine(week_monday(activity_filter.end) + timedelta(days=7), time.min)
    if bounds:
        match["startTimeLocal"] = bounds
    return match


def weekly_pipeline(activity_filter: ActivityFilter, fields: dict, accumulator: str = "$sum") -> list[dict]:
    """Builds a pipeline returning one document per ISO week with runs.

    Args:
        activity_filter: Activities to include.
        fields: Output field names mapped to a $project expression (1 keeps the raw field).
        accumulator: How runs of a week combine, e.g. "$sum" or "$avg".
    """
    return [
        {"$match": activity_match(activity_filter)},
        {"$project": {
            "year": {"$isoWeekYear": "$startTimeLocal"},
            "week": {"$isoWeek": "$startTimeLocal"},
            **fields,
        }},
        {"$group": {
            "_id": WEEK_GROUP_ID,
            **{name: {accumulator: f"${name}"} for name in fields},
        }},
    ]


def date_range_pipeline(activity_filter: ActivityFilter) -> list[dict]:
    return [
        {"$match": activity_match(activity_filter)},
        {"$group": {"_id": None, "first": {"$min": "$startTimeLocal"}, "last": {"$max": "$startTimeLocal"}}},
    ]


def get_metric_list_pipeline_by_activity(year: int, week: int, metric_list: list, types: tuple[int, ...]) -> list[dict]:
    return [
        {"$match": activity_match(ActivityFilter(types=types))},
        {"$project": {
            "year": {"$isoWeekYear": "$startTimeLocal"},
            "week": {"$isoWeek": "$startTimeLocal"},
            **{metric: 1 for metric in metric_list},
        }},
        {"$match": {"year": year, "week": week}},
        {"$sort": {"startTimeLocal": 1}},
        {"$group": {
            "_id": None,
            **{metric: {"$push": f"${metric}"} for metric in metric_list},
        }},
    ]


def get_week_types_pipeline() -> list[dict]:
    return [
        {"$lookup": {
            "from": "weekTypes",
            "localField": "weekTypeId",
            "foreignField": "weekTypeId",
            "as": "label",
        }},
        {"$unwind": {"path": "$label"}},
        {"$project": {"_id": 0, "date": 1, "label": "$label.label"}},
    ]
