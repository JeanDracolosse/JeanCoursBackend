"""Shared test setup.

mongo.py connects to MongoDB as soon as it is imported, so the real client is
replaced by an in-memory mongomock client here, before any test module
imports the application code.
"""
from datetime import datetime

import mongomock
import pymongo
import pytest
from mongomock import aggregate as mongomock_aggregate

_in_memory_client = mongomock.MongoClient()
pymongo.MongoClient = lambda *args, **kwargs: _in_memory_client

# mongomock does not implement $isoWeek / $isoWeekYear, which every weekly
# pipeline uses. Both map directly onto Python's ISO calendar.
_original_handle_date_operator = mongomock_aggregate._Parser._handle_date_operator


def _handle_date_operator(self, operator, values):
    if operator in ("$isoWeek", "$isoWeekYear"):
        value = self.parse(values)
        if value is None:
            return None
        iso_year, iso_week, _ = value.isocalendar()
        return iso_week if operator == "$isoWeek" else iso_year
    return _original_handle_date_operator(self, operator, values)


mongomock_aggregate._Parser._handle_date_operator = _handle_date_operator

import mongo  # noqa: E402  (must be imported after the client is patched)


@pytest.fixture(autouse=True)
def empty_database():
    for collection_name in mongo.database.list_collection_names():
        mongo.database[collection_name].delete_many({})
    yield


def _activity(activity_id, start, type_id=1, **fields):
    return {
        "activityId": activity_id,
        "activityType": {"typeId": type_id},
        "startTimeLocal": start,
        **fields,
    }


@pytest.fixture
def two_weeks_of_runs():
    """Runs in ISO weeks 10 and 11 of 2025, plus one non-running activity.

    Inserted out of order so that tests also check the pipelines' sorting.
    """
    mongo.activities_collection.insert_many([
        _activity(3, datetime(2025, 3, 10, 8), type_id=1,
                  distance=8000, elevationGain=20, elevationLoss=20, averageHR=160,
                  hrTimeInZone_1=1, hrTimeInZone_2=2, hrTimeInZone_3=3, hrTimeInZone_4=4, hrTimeInZone_5=5,
                  powerTimeInZone_1=0, powerTimeInZone_2=0, powerTimeInZone_3=0, powerTimeInZone_4=0, powerTimeInZone_5=10),
        _activity(2, datetime(2025, 3, 5, 18), type_id=6,
                  distance=5000, elevationGain=0, elevationLoss=0, averageHR=140,
                  hrTimeInZone_1=10, hrTimeInZone_2=20, hrTimeInZone_3=30, hrTimeInZone_4=40, hrTimeInZone_5=50,
                  powerTimeInZone_1=1, powerTimeInZone_2=2, powerTimeInZone_3=3, powerTimeInZone_4=4, powerTimeInZone_5=5),
        _activity(1, datetime(2025, 3, 3, 8), type_id=1,
                  distance=10000, elevationGain=100, elevationLoss=50, averageHR=150,
                  hrTimeInZone_1=60, hrTimeInZone_2=120, hrTimeInZone_3=180, hrTimeInZone_4=240, hrTimeInZone_5=300,
                  powerTimeInZone_1=5, powerTimeInZone_2=5, powerTimeInZone_3=5, powerTimeInZone_4=5, powerTimeInZone_5=5),
        _activity(4, datetime(2025, 3, 5, 12), type_id=2,
                  distance=40000, elevationGain=300, elevationLoss=300, averageHR=130),
    ])
