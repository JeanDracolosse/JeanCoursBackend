from datetime import date, datetime

import pytest

from jean_cours import db
from jean_cours.stats import weekly
from jean_cours.stats.pipelines import ActivityFilter
from jean_cours.stats.training_load import hr_tss


def whenGetDistance_thenSumsDistanceAndEffortPerWeekForRunsOnly(two_weeks_of_runs):
    # Given
    # When
    result = weekly.get_distance()

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
    result = weekly.get_hr_time_in_zone()

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
    result = weekly.get_power_time_in_zone()

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
    result = weekly.get_cumulative_metric_list_by_week(metrics)

    # Then
    assert result == {"distance": [15000, 8000], "elevationGain": [100, 20]}


def whenGetAverageMetricListByWeek_thenAveragesEachMetricPerWeek(two_weeks_of_runs):
    # Given
    metrics = ["averageHR"]

    # When
    result = weekly.get_average_metric_list_by_week(metrics)

    # Then
    assert result == {"averageHR": [147.5, 160]}


def whenGetMetricListByActivity_thenReturnsRunsOfThatWeekSortedByStartTime(two_weeks_of_runs):
    # Given
    metrics = ["distance"]

    # When
    result = weekly.get_metric_list_by_activity(2025, 10, metrics)

    # Then
    assert result == {
        "distance": [10000, 5000],
        "startTimeLocal": [datetime(2025, 3, 3, 8), datetime(2025, 3, 5, 18)],
    }


def whenGetDistance_thenReturnsEmptyArraysWithoutRuns():
    # Given
    # When
    result = weekly.get_distance()

    # Then
    assert result == {"distance": [], "elevationGain": [], "elevationLoss": [],
                      "kilometerEffort": [], "fullKilometerEffort": []}


def whenGetHrTimeInZone_thenReturnsEmptyArraysWithoutRuns():
    # Given
    # When
    result = weekly.get_hr_time_in_zone()

    # Then
    assert result == {f"hrTimeInZone_{zone}": [] for zone in range(1, 6)}


def whenGetPowerTimeInZone_thenReturnsEmptyArraysWithoutRuns():
    # Given
    # When
    result = weekly.get_power_time_in_zone()

    # Then
    assert result == {f"powerTimeInZone_{zone}": [] for zone in range(1, 6)}


def whenGetAverageMetricListByWeek_thenReturnsEmptyArraysWithoutRuns():
    # Given
    # When
    result = weekly.get_average_metric_list_by_week(["averageHR"])

    # Then
    assert result == {"averageHR": []}


def whenGetCumulativeMetricListByWeek_thenReturnsEmptyArraysWithoutRuns():
    # Given
    # When
    result = weekly.get_cumulative_metric_list_by_week(["distance"])

    # Then
    assert result == {"distance": []}


def whenGetMetricListByActivity_thenReturnsEmptyArraysForWeekWithoutRuns(two_weeks_of_runs):
    # Given
    # When
    result = weekly.get_metric_list_by_activity(2025, 30, ["distance"])

    # Then
    assert result == {"distance": [], "startTimeLocal": []}


def whenGetIndexes_thenReturnsOneEntryPerWeekWithRuns(two_weeks_of_runs):
    # Given
    # When
    result = weekly.get_indexes()

    # Then
    assert len(result) == 2


def whenGetIndexes_thenReturnsMondayOfEachIsoWeek(two_weeks_of_runs):
    # Given
    # When
    result = weekly.get_indexes()

    # Then
    assert result == [datetime(2025, 3, 3), datetime(2025, 3, 10)]


def whenGetIndexes_thenUsesIsoYearForWeeksSpanningNewYear():
    # Given
    db.activities_collection.insert_one(
        {"activityId": 1, "activityType": {"typeId": 1}, "startTimeLocal": datetime(2025, 12, 31, 8)})

    # When
    result = weekly.get_indexes()

    # Then
    assert result == [datetime(2025, 12, 29)]


def whenGetDistance_thenWeeksAreInChronologicalOrder():
    # Given
    db.activities_collection.insert_many([
        {"activityId": 1, "activityType": {"typeId": 1}, "startTimeLocal": datetime(2025, 2, 24, 8),
         "distance": 9000, "elevationGain": 0, "elevationLoss": 0},
        {"activityId": 2, "activityType": {"typeId": 1}, "startTimeLocal": datetime(2025, 3, 3, 8),
         "distance": 10000, "elevationGain": 0, "elevationLoss": 0},
    ])

    # When
    result = weekly.get_distance()

    # Then
    assert result["distance"] == [9000, 10000]


def whenGetIndexes_thenWeeksAreInChronologicalOrderAcrossYears():
    # Given
    db.activities_collection.insert_many([
        {"activityId": 1, "activityType": {"typeId": 1}, "startTimeLocal": datetime(2026, 1, 5, 8)},
        {"activityId": 2, "activityType": {"typeId": 1}, "startTimeLocal": datetime(2025, 12, 22, 8)},
        {"activityId": 3, "activityType": {"typeId": 1}, "startTimeLocal": datetime(2025, 12, 31, 8)},
    ])

    # When
    result = weekly.get_indexes()

    # Then
    assert result == [datetime(2025, 12, 22), datetime(2025, 12, 29), datetime(2026, 1, 5)]


def _run(activity_id, start, type_id=1, **fields):
    return {"activityId": activity_id, "activityType": {"typeId": type_id}, "startTimeLocal": start, **fields}


def whenGetIndexes_thenListsWeeksWithoutRuns():
    # Given
    db.activities_collection.insert_many([
        _run(1, datetime(2025, 3, 3, 8)),
        _run(2, datetime(2025, 3, 19, 8)),
    ])

    # When
    result = weekly.get_indexes()

    # Then
    assert result == [datetime(2025, 3, 3), datetime(2025, 3, 10), datetime(2025, 3, 17)]


def whenGetDistance_thenFillsWeeksWithoutRunsWithZero():
    # Given
    db.activities_collection.insert_many([
        _run(1, datetime(2025, 3, 3, 8), distance=10000, elevationGain=0, elevationLoss=0),
        _run(2, datetime(2025, 3, 19, 8), distance=8000, elevationGain=0, elevationLoss=0),
    ])

    # When
    result = weekly.get_distance()

    # Then
    assert result["distance"] == [10000, 0, 8000]


def whenGetAverageMetricListByWeek_thenFillsWeeksWithoutRunsWithNull():
    # Given
    db.activities_collection.insert_many([
        _run(1, datetime(2025, 3, 3, 8), averageHR=150, duration=3600),
        _run(2, datetime(2025, 3, 19, 8), averageHR=160, duration=3600),
    ])

    # When
    result = weekly.get_average_metric_list_by_week(["averageHR"])

    # Then
    assert result == {"averageHR": [150, None, 160]}


def whenGetDistance_thenOnlyCountsRunsInsideTheRange(two_weeks_of_runs):
    # Given
    activity_filter = ActivityFilter(start=date(2025, 3, 12), end=date(2025, 3, 12))

    # When
    result = weekly.get_distance(activity_filter)

    # Then
    assert result["distance"] == [8000]


def whenGetDistance_thenZeroFillsTheWholeRequestedRange(two_weeks_of_runs):
    # Given
    activity_filter = ActivityFilter(start=date(2025, 2, 24), end=date(2025, 3, 17))

    # When
    distance = weekly.get_distance(activity_filter)
    indexes = weekly.get_indexes(activity_filter)

    # Then
    assert distance["distance"] == [0, 15000, 8000, 0]
    assert indexes == [datetime(2025, 2, 24), datetime(2025, 3, 3), datetime(2025, 3, 10), datetime(2025, 3, 17)]


def whenGetDistance_thenUsesRequestedActivityTypes(two_weeks_of_runs):
    # Given
    activity_filter = ActivityFilter(types=(2,))

    # When
    result = weekly.get_distance(activity_filter)

    # Then
    assert result["distance"] == [40000]


def whenGetAverageMetricListByWeek_thenWeightsRunsByDuration():
    # Given
    db.activities_collection.insert_many([
        _run(1, datetime(2025, 3, 3, 8), averageHR=150, duration=1800),
        _run(2, datetime(2025, 3, 4, 8), averageHR=160, duration=7200),
    ])

    # When
    result = weekly.get_average_metric_list_by_week(["averageHR"])

    # Then
    assert result == {"averageHR": [158]}


def whenGetAverageMetricListByWeek_thenIgnoresRunsWithoutTheMetric():
    # Given
    db.activities_collection.insert_many([
        _run(1, datetime(2025, 3, 3, 8), averageHR=150, duration=1800),
        _run(2, datetime(2025, 3, 4, 8), duration=7200),
    ])

    # When
    result = weekly.get_average_metric_list_by_week(["averageHR"])

    # Then
    assert result == {"averageHR": [150]}


def whenGetAverageMetricListByWeek_thenReturnsNullForWeekWhereNoRunHasTheMetric():
    # Given
    db.activities_collection.insert_many([
        _run(1, datetime(2025, 3, 3, 8), duration=1800),
    ])

    # When
    result = weekly.get_average_metric_list_by_week(["averageHR"])

    # Then
    assert result == {"averageHR": [None]}


THRESHOLD = {"date": "2025-01-01", "lthr": 170, "restingHr": 50, "maxHr": 190, "trimpA": 0.64, "trimpB": 1.92}


def whenGetTrainingLoad_thenIsAlignedWithIndexes(two_weeks_of_runs):
    # Given
    db.upsert_threshold(THRESHOLD)
    threshold = weekly.get_thresholds()[0]

    # When
    result = weekly.get_training_load()

    # Then
    assert len(result["tss"]) == len(weekly.get_indexes()) == 2
    assert result["tss"][0] == pytest.approx(hr_tss(2700, 150, threshold) + hr_tss(900, 140, threshold))
    assert result["tss"][1] == pytest.approx(hr_tss(3000, 160, threshold))


def whenGetTrainingLoadByDay_thenWarmsUpCtlFromRunsBeforeTheRange(two_weeks_of_runs):
    # Given
    db.upsert_threshold(THRESHOLD)

    # When
    result = weekly.get_training_load_by_day(ActivityFilter(start=date(2025, 3, 10), end=date(2025, 3, 16)))

    # Then
    assert result["date"][0] == date(2025, 3, 10)
    assert len(result["date"]) == 7
    assert result["ctl"][0] > 0


def whenGetTrainingLoad_thenRaisesWithoutThresholds(two_weeks_of_runs):
    # Given
    # When
    with pytest.raises(weekly.NoThresholds):
        weekly.get_training_load()

    # Then


def whenGetMetricListByActivity_thenDoesNotChangeTheMetricList(two_weeks_of_runs):
    # Given
    metrics = ["distance"]

    # When
    weekly.get_metric_list_by_activity(2025, 10, metrics)

    # Then
    assert metrics == ["distance"]


def whenGetWeekTypes_thenReturnsEachWeekWithItsTypeLabel():
    # Given
    db.upsert_week_type({"weekTypeId": 0, "label": "Base"})
    db.upsert_week_type({"weekTypeId": 1, "label": "Récupération"})
    db.upsert_week({"date": "2025-11-10", "weekTypeId": 1})

    # When
    result = weekly.get_week_types()

    # Then
    assert result == [{"date": "2025-11-10", "label": "Récupération"}]


def whenUpsertActivity_thenMergesFieldsIntoTheExistingActivity():
    # Given
    db.upsert_activity({"activityId": 1, "distance": 10000})

    # When
    db.upsert_activity({"activityId": 1, "workoutRpe": 30})

    # Then
    activities = list(db.activities_collection.find({}, {"_id": 0}))
    assert activities == [{"activityId": 1, "distance": 10000, "workoutRpe": 30}]


def whenGetLastDate_thenReturnsTodayWhenNothingIsStored():
    # Given
    # When
    result = db.get_last_date()

    # Then
    assert result == date.today()


def whenGetLastDate_thenReturnsTheStoredDate():
    # Given
    db.configuration_collection.insert_one({"lastDate": "2025-03-01"})

    # When
    result = db.get_last_date()

    # Then
    assert result == date(2025, 3, 1)


def whenSetLastDate_thenStoresTodayAsIsoString():
    # Given
    db.configuration_collection.insert_one({"lastDate": "2025-03-01"})

    # When
    db.set_last_date()

    # Then
    configurations = list(db.configuration_collection.find({}, {"_id": 0}))
    assert configurations == [{"lastDate": date.today().isoformat()}]
