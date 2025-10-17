from pymongo import MongoClient, ASCENDING
from pymongo.server_api import ServerApi
from pymongo.database import Database
from pymongo.collection import Collection

import os
from dotenv import load_dotenv
from datetime import date, datetime

from aggregation import DISTANCE_PIPELINE, HR_TIME_IN_ZONE_PIPELINE, INDEX_PIPELINE, POWER_TIME_IN_ZONE_PIPELINE, get_cumulative_metric_list_pipeline_by_week, get_cumulative_metric_list_pipeline_by_activity

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


def upsert_activity(activity: dict) -> None:
    activities_collection.update_one({"activityId": activity['activityId']}, {
                                     "$set": activity}, upsert=True)

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


def get_indexes() -> None:
    return [datetime.strptime(index['_id'] + '-1', "%Y-%W-%w") for index in __aggregate_activities_pipeline(INDEX_PIPELINE)]


def get_hr_time_in_zone() -> None:
    return __aggregate_activities_pipeline(HR_TIME_IN_ZONE_PIPELINE)[0]


def get_power_time_in_zone() -> None:
    return __aggregate_activities_pipeline(POWER_TIME_IN_ZONE_PIPELINE)[0]


def get_distance() -> None:
    return __aggregate_activities_pipeline(DISTANCE_PIPELINE)[0]


def __aggregate_activities_pipeline(pipeline: dict) -> dict:
    cursor = activities_collection.aggregate(pipeline)
    return [data for data in cursor]


def get_metric_list_by_week(metric_list: list) -> None:
    return __aggregate_activities_pipeline(get_cumulative_metric_list_pipeline_by_week(metric_list))[0]


def get_metric_list_by_activity(year: int, week: int, metric_list: list) -> None:
    if "startTimeLocal" not in metric_list:
        metric_list.append("startTimeLocal")
    return __aggregate_activities_pipeline(get_cumulative_metric_list_pipeline_by_activity(year, week, metric_list))[0]

