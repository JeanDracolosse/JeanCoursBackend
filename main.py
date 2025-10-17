from typing import Annotated, Optional
from fastapi import FastAPI, Query
from activity import update_fit
from mongo import get_distance, get_hr_time_in_zone, get_indexes, get_metric_list_by_activity, get_metric_list_by_week, get_power_time_in_zone
app = FastAPI()


@app.get("/hrTimeInZone")
async def root():
    return get_hr_time_in_zone()


@app.get("/powerTimeInZone")
async def root():
    return get_power_time_in_zone()


@app.get("/distance")
async def root():
    return get_distance()


@app.get("/index")
async def root():
    return get_indexes()


@app.get("/metricsByWeek")
async def get_metrics(metrics: Annotated[list, Query()]):
    if metrics:
        return get_metric_list_by_week(metrics)
    return []


@app.get("/metricsByActivity")
async def get_metrics(year: Annotated[int, Query()], week: Annotated[int, Query()] = [], metrics: Annotated[list, Query()] = []):
    if year and week and metrics:
        return get_metric_list_by_activity(year, week, metrics)
    return []


@app.get("/garmin")
async def root():
    return update_fit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
