"""MongoDB connection, collections and writes.

Importing this module only resolves the cluster's DNS record (mongodb+srv).
pymongo connects on the first query. Nothing is written at import.
"""
import os
from datetime import date

from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient
from pymongo.database import Database
from pymongo.server_api import ServerApi

load_dotenv()


def _get_database() -> Database:
    uri = (f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_URL')}"
           f"/?retryWrites=true&w=majority&appName={os.getenv('MONGO_APP_NAME')}")
    return MongoClient(uri, server_api=ServerApi("1")).jeanCours


database = _get_database()
activities_collection = database.get_collection("activities")
configuration_collection = database.get_collection("configuration")
week_type_collection = database.get_collection("weekTypes")
week_collection = database.get_collection("weeks")
threshold_collection = database.get_collection("thresholds")

UNIQUE_INDEXES = {
    activities_collection: "activityId",
    week_type_collection: "weekTypeId",
    week_collection: "date",
    threshold_collection: "date",
}


def ensure_indexes() -> None:
    """Creates the unique indexes. Needs write access, so the read-only web API never calls it.

    Idempotent: existing indexes are left as they are.
    """
    for collection, field in UNIQUE_INDEXES.items():
        collection.create_index([(field, ASCENDING)], unique=True)


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
