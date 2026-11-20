"""MongoDB connection, collections and writes. Connects on import."""
import os
from datetime import date

from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.server_api import ServerApi

load_dotenv()


def _get_database() -> Database:
    uri = (f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_URL')}"
           f"/?retryWrites=true&w=majority&appName={os.getenv('MONGO_APP_NAME')}")
    return MongoClient(uri, server_api=ServerApi("1")).jeanCours


def _collection(name: str, unique_field: str | None = None) -> Collection:
    collection = database.get_collection(name)
    if unique_field:
        # Idempotent: a no-op when the index already exists.
        collection.create_index([(unique_field, ASCENDING)], unique=True)
    return collection


database = _get_database()
activities_collection = _collection("activities", "activityId")
configuration_collection = _collection("configuration")
week_type_collection = _collection("weekTypes", "weekTypeId")
week_collection = _collection("weeks", "date")
threshold_collection = _collection("thresholds", "date")


def upsert_activity(activity: dict) -> None:
    activities_collection.update_one({"activityId": activity["activityId"]}, {"$set": activity}, upsert=True)


def upsert_week_type(week_type: dict) -> None:
    week_type_collection.update_one({"weekTypeId": week_type["weekTypeId"]}, {"$set": week_type}, upsert=True)


def upsert_week(week: dict) -> None:
    week_collection.update_one({"date": week["date"]}, {"$set": week}, upsert=True)


def upsert_threshold(threshold: dict) -> None:
    threshold_collection.update_one({"date": threshold["date"]}, {"$set": threshold}, upsert=True)


def get_last_date() -> date:
    """Returns the date of the last sync, or today if none."""
    configuration = configuration_collection.find_one()
    if configuration is None:
        return date.today()
    return date.fromisoformat(configuration["lastDate"])


def set_last_date() -> None:
    configuration_collection.update_many({}, {"$set": {"lastDate": date.today().isoformat()}}, upsert=True)
