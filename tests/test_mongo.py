from datetime import date, datetime

import mongo


def whenGetDistance_thenSumsDistanceAndEffortPerWeekForRunsOnly(two_weeks_of_runs):
    # Given
    # When
    result = mongo.get_distance()

    # Then
    assert result == {
        "distance": [15000, 8000],
        "elevationGain": [100, 20],
        "elevationLoss": [50, 20],
        "kilometerEffort": [16000, 8200],
        "fullKilometerEffort": [16150, 8260],
    }


def whenGetHrTimeInZone_thenSumsEachZonePerWeek(two_weeks_of_runs):
    # Given
    # When
    result = mongo.get_hr_time_in_zone()

    # Then
    assert result == {
        "hrTimeInZone_1": [70, 1],
        "hrTimeInZone_2": [140, 2],
        "hrTimeInZone_3": [210, 3],
        "hrTimeInZone_4": [280, 4],
        "hrTimeInZone_5": [350, 5],
    }


def whenGetPowerTimeInZone_thenSumsEachZonePerWeek(two_weeks_of_runs):
    # Given
    # When
    result = mongo.get_power_time_in_zone()

    # Then
    assert result == {
        "powerTimeInZone_1": [6, 0],
        "powerTimeInZone_2": [7, 0],
        "powerTimeInZone_3": [8, 0],
        "powerTimeInZone_4": [9, 0],
        "powerTimeInZone_5": [10, 10],
    }


def whenGetCumulativeMetricListByWeek_thenSumsEachMetricPerWeek(two_weeks_of_runs):
    # Given
    metrics = ["distance", "elevationGain"]

    # When
    result = mongo.get_cumulative_metric_list_by_week(metrics)

    # Then
    assert result == {"distance": [15000, 8000], "elevationGain": [100, 20]}


def whenGetAverageMetricListByWeek_thenAveragesEachMetricPerWeek(two_weeks_of_runs):
    # Given
    metrics = ["averageHR"]

    # When
    result = mongo.get_average_metric_list_by_week(metrics)

    # Then
    assert result == {"averageHR": [145, 160]}


def whenGetMetricListByActivity_thenReturnsRunsOfThatWeekSortedByStartTime(two_weeks_of_runs):
    # Given
    metrics = ["distance"]

    # When
    result = mongo.get_metric_list_by_activity(2025, 10, metrics)

    # Then
    assert result == {
        "distance": [10000, 5000],
        "startTimeLocal": [datetime(2025, 3, 3, 8), datetime(2025, 3, 5, 18)],
    }


def whenGetDistance_thenReturnsEmptyArraysWithoutRuns():
    # Given
    # When
    result = mongo.get_distance()

    # Then
    assert result == {"distance": [], "elevationGain": [], "elevationLoss": [],
                      "kilometerEffort": [], "fullKilometerEffort": []}


def whenGetHrTimeInZone_thenReturnsEmptyArraysWithoutRuns():
    # Given
    # When
    result = mongo.get_hr_time_in_zone()

    # Then
    assert result == {f"hrTimeInZone_{zone}": [] for zone in range(1, 6)}


def whenGetPowerTimeInZone_thenReturnsEmptyArraysWithoutRuns():
    # Given
    # When
    result = mongo.get_power_time_in_zone()

    # Then
    assert result == {f"powerTimeInZone_{zone}": [] for zone in range(1, 6)}


def whenGetAverageMetricListByWeek_thenReturnsEmptyArraysWithoutRuns():
    # Given
    # When
    result = mongo.get_average_metric_list_by_week(["averageHR"])

    # Then
    assert result == {"averageHR": []}


def whenGetCumulativeMetricListByWeek_thenReturnsEmptyArraysWithoutRuns():
    # Given
    # When
    result = mongo.get_cumulative_metric_list_by_week(["distance"])

    # Then
    assert result == {"distance": []}


def whenGetMetricListByActivity_thenReturnsEmptyArraysForWeekWithoutRuns(two_weeks_of_runs):
    # Given
    # When
    result = mongo.get_metric_list_by_activity(2025, 30, ["distance"])

    # Then
    assert result == {"distance": [], "startTimeLocal": []}


def whenGetIndexes_thenReturnsOneEntryPerWeekWithRuns(two_weeks_of_runs):
    # Given
    # When
    result = mongo.get_indexes()

    # Then
    assert len(result) == 2


def whenGetIndexes_thenReturnsMondayOfEachIsoWeek(two_weeks_of_runs):
    # Given
    # When
    result = mongo.get_indexes()

    # Then
    assert result == [datetime(2025, 3, 3), datetime(2025, 3, 10)]


def whenGetIndexes_thenUsesIsoYearForWeeksSpanningNewYear():
    # Given
    mongo.activities_collection.insert_one(
        {"activityId": 1, "activityType": {"typeId": 1}, "startTimeLocal": datetime(2025, 12, 31, 8)})

    # When
    result = mongo.get_indexes()

    # Then
    assert result == [datetime(2025, 12, 29)]


def whenGetDistance_thenWeeksAreInChronologicalOrder():
    # Given
    mongo.activities_collection.insert_many([
        {"activityId": 1, "activityType": {"typeId": 1}, "startTimeLocal": datetime(2025, 2, 24, 8),
         "distance": 9000, "elevationGain": 0, "elevationLoss": 0},
        {"activityId": 2, "activityType": {"typeId": 1}, "startTimeLocal": datetime(2025, 3, 3, 8),
         "distance": 10000, "elevationGain": 0, "elevationLoss": 0},
    ])

    # When
    result = mongo.get_distance()

    # Then
    assert result["distance"] == [9000, 10000]


def whenGetIndexes_thenWeeksAreInChronologicalOrderAcrossYears():
    # Given
    mongo.activities_collection.insert_many([
        {"activityId": 1, "activityType": {"typeId": 1}, "startTimeLocal": datetime(2026, 3, 2, 8)},
        {"activityId": 2, "activityType": {"typeId": 1}, "startTimeLocal": datetime(2025, 12, 22, 8)},
        {"activityId": 3, "activityType": {"typeId": 1}, "startTimeLocal": datetime(2026, 1, 5, 8)},
    ])

    # When
    result = mongo.get_indexes()

    # Then
    assert result == [datetime(2025, 12, 22), datetime(2026, 1, 5), datetime(2026, 3, 2)]


def whenGetWeekTypes_thenReturnsEachWeekWithItsTypeLabel():
    # Given
    mongo.upsert_week_type({"weekTypeId": 0, "label": "Base"})
    mongo.upsert_week_type({"weekTypeId": 1, "label": "Récupération"})
    mongo.upsert_week({"date": "2025-11-10", "weekTypeId": 1})

    # When
    result = mongo.get_week_types()

    # Then
    assert result == [{"date": "2025-11-10", "label": "Récupération"}]


def whenUpsertActivity_thenMergesFieldsIntoTheExistingActivity():
    # Given
    mongo.upsert_activity({"activityId": 1, "distance": 10000})

    # When
    mongo.upsert_activity({"activityId": 1, "workoutRpe": 30})

    # Then
    activities = list(mongo.activities_collection.find({}, {"_id": 0}))
    assert activities == [{"activityId": 1, "distance": 10000, "workoutRpe": 30}]


def whenGetLastDate_thenReturnsTodayWhenNothingIsStored():
    # Given
    # When
    result = mongo.get_last_date()

    # Then
    assert result == date.today()


def whenGetLastDate_thenReturnsTheStoredDate():
    # Given
    mongo.configuration_collection.insert_one({"lastDate": "2025-03-01"})

    # When
    result = mongo.get_last_date()

    # Then
    assert result == date(2025, 3, 1)


def whenSetLastDate_thenStoresTodayAsIsoString():
    # Given
    mongo.configuration_collection.insert_one({"lastDate": "2025-03-01"})

    # When
    mongo.set_last_date()

    # Then
    configurations = list(mongo.configuration_collection.find({}, {"_id": 0}))
    assert configurations == [{"lastDate": date.today().isoformat()}]
