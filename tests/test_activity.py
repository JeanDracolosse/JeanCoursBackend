from datetime import date

import activity
import mongo


def whenUpdateFit_thenStoresActivitiesWithFitDataAndMovesLastDateToToday(monkeypatch):
    # Given
    mongo.configuration_collection.insert_one({"lastDate": "2025-03-01"})
    requested_dates = []

    def fake_fetch_from_date(start_date):
        requested_dates.append(start_date)
        return [{"activityId": 1, "distance": 10000}]

    monkeypatch.setattr(activity, "fetch_from_date", fake_fetch_from_date)
    monkeypatch.setattr(activity, "download_fit_from_id",
                        lambda activity_id: {"activityId": activity_id, "workoutFeel": 50, "workoutRpe": 30})

    # When
    activity.update_fit()

    # Then
    assert requested_dates == [date(2025, 3, 1)]
    activities = list(mongo.activities_collection.find({}, {"_id": 0}))
    assert activities == [{"activityId": 1, "distance": 10000, "workoutFeel": 50, "workoutRpe": 30}]
    assert mongo.get_last_date() == date.today()
