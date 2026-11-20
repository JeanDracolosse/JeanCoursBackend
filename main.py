from datetime import date, datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from activity import update_fit
from aggregation import RUNNING_TYPES, ActivityFilter
from garmin import GarminLoginRequired
from mongo import (NoThresholds, get_average_metric_list_by_week, get_cumulative_metric_list_by_week, get_distance,
                   get_hr_time_in_zone, get_indexes, get_metric_list_by_activity, get_power_time_in_zone,
                   get_training_load, get_training_load_by_day, get_week_types)
from schemas import (ActivityMetrics, DistanceWeeks, ErrorDetail, HrTimeInZoneWeeks, PowerTimeInZoneWeeks,
                     TrainingLoadDays, TrainingLoadWeeks, WeeklyMetrics, WeekType)

app = FastAPI(
    title="Jean Cours API",
    description="Running stats from Garmin. Weekly arrays share one order: the weeks listed by `/index`.",
    version="1.0.0",
)


@app.exception_handler(NoThresholds)
async def no_thresholds_handler(request: Request, error: NoThresholds):
    return JSONResponse(status_code=409, content={"detail": str(error)})


NO_THRESHOLDS = {409: {"model": ErrorDetail, "description": "No heart-rate threshold stored. Run `setThresholds.py`."}}

WEEKLY = "Weekly stats"
DAILY = "Daily stats"
SYNC = "Sync"
PLANNING = "Planning"

Metrics = Annotated[list[str], Query(
    description="Garmin activity field names. Repeat the parameter for several.",
    examples=[["distance", "elevationGain"]],
)]

Types = Annotated[list[int], Query(description="Garmin activity type ids. Default: running types 1 and 6.")]


def activity_filter(
    start: Annotated[date | None, Query(alias="from", description="First day of the range. Its whole week is included.")] = None,
    end: Annotated[date | None, Query(alias="to", description="Last day of the range. Its whole week is included.")] = None,
    types: Types = list(RUNNING_TYPES),
) -> ActivityFilter:
    if start and end and start > end:
        raise HTTPException(status_code=422, detail="'from' must be on or before 'to'.")
    return ActivityFilter(start, end, tuple(types))


Filter = Annotated[ActivityFilter, Depends(activity_filter)]


@app.get("/index", tags=[WEEKLY], response_model=list[datetime],
         summary="Weeks with runs", description="Monday of every ISO week in the range, oldest first, including weeks without runs.")
async def index(activity_filter: Filter):
    return get_indexes(activity_filter)


@app.get("/distance", tags=[WEEKLY], response_model=DistanceWeeks, summary="Distance and elevation per week")
async def distance(activity_filter: Filter):
    return get_distance(activity_filter)


@app.get("/hrTimeInZone", tags=[WEEKLY], response_model=HrTimeInZoneWeeks, summary="Time in heart rate zones per week")
async def hr_time_in_zone(activity_filter: Filter):
    return get_hr_time_in_zone(activity_filter)


@app.get("/powerTimeInZone", tags=[WEEKLY], response_model=PowerTimeInZoneWeeks, summary="Time in power zones per week")
async def power_time_in_zone(activity_filter: Filter):
    return get_power_time_in_zone(activity_filter)


@app.get("/metricsSumByWeek", tags=[WEEKLY], response_model=WeeklyMetrics,
         summary="Sum of metrics per week", description="One array per requested metric, aligned with `/index`. Weeks without runs are 0.")
async def metrics_sum_by_week(metrics: Metrics, activity_filter: Filter):
    return get_cumulative_metric_list_by_week(metrics, activity_filter)


@app.get("/metricsAvgByWeek", tags=[WEEKLY], response_model=WeeklyMetrics,
         summary="Average of metrics per week, weighted by duration",
         description="One array per requested metric, aligned with `/index`. Each run counts in proportion to its `duration`; "
                     "runs without the metric are ignored. `null` for weeks where no run has it.")
async def metrics_avg_by_week(metrics: Metrics, activity_filter: Filter):
    return get_average_metric_list_by_week(metrics, activity_filter)


@app.get("/trainingLoad", tags=[WEEKLY], response_model=TrainingLoadWeeks, responses=NO_THRESHOLDS,
         summary="TSS, CTL, ATL and TSB per week")
async def training_load(activity_filter: Filter):
    return get_training_load(activity_filter)


@app.get("/trainingLoadByDay", tags=[DAILY], response_model=TrainingLoadDays, responses=NO_THRESHOLDS,
         summary="TSS, CTL, ATL and TSB per day")
async def training_load_by_day(activity_filter: Filter):
    return get_training_load_by_day(activity_filter)


@app.get("/metricsByActivity", tags=[WEEKLY], response_model=ActivityMetrics,
         summary="Metrics of each run in a week",
         description="One array per requested metric, one value per run, sorted by start time. `startTimeLocal` is always included.")
async def metrics_by_activity(
    year: Annotated[int, Query(description="ISO week year.", examples=[2025])],
    week: Annotated[int, Query(description="ISO week number.", ge=1, le=53, examples=[10])],
    metrics: Metrics,
    types: Types = list(RUNNING_TYPES),
):
    return get_metric_list_by_activity(year, week, metrics, tuple(types))


@app.get("/weekTypes", tags=[PLANNING], response_model=list[WeekType], summary="Planned type of each week")
async def week_types():
    return get_week_types()


@app.get("/garmin", tags=[SYNC], response_model=None, summary="Sync new activities from Garmin",
         description="Fetches activities since the last sync and stores them.",
         responses={401: {"model": ErrorDetail, "description": "Garmin needs an MFA code. Run `activity.py` in a terminal."}})
def sync_garmin():
    try:
        update_fit()
    except GarminLoginRequired as error:
        raise HTTPException(status_code=401, detail=str(error))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
