from datetime import date

import activity
import mongo


def whenUpdateFit_thenStoresActivitiesWithFitDataAndMovesLastDateToToday(monkeypatch):
    # Given
    mongo.configuration_collection.insert_one({"lastDate": "2025-03-01"})
    requested_dates = []

    def fake_fetch_from_date(client, start_date, until=None):
        requested_dates.append(start_date)
        return [{"activityId": 1, "distance": 10000}]

    monkeypatch.setattr(activity, "login", lambda interactive: "client")
    monkeypatch.setattr(activity, "fetch_from_date", fake_fetch_from_date)
    monkeypatch.setattr(activity, "download_fit_from_id",
                        lambda client, activity_id: {"activityId": activity_id, "workoutFeel": 50, "workoutRpe": 30})

    # When
    activity.update_fit()

    # Then
    assert requested_dates == [date(2025, 3, 1)]
    activities = list(mongo.activities_collection.find({}, {"_id": 0}))
    assert activities == [{"activityId": 1, "distance": 10000, "workoutFeel": 50, "workoutRpe": 30}]
    assert mongo.get_last_date() == date.today()


def whenUpdateFit_thenFetchesFromSinceWhenGiven(monkeypatch):
    # Given
    mongo.configuration_collection.insert_one({"lastDate": "2025-03-01"})
    requested_dates = []

    def fake_fetch_from_date(client, start_date, until=None):
        requested_dates.append(start_date)
        return []

    monkeypatch.setattr(activity, "login", lambda interactive: "client")
    monkeypatch.setattr(activity, "fetch_from_date", fake_fetch_from_date)

    # When
    activity.update_fit(since=date(2015, 1, 1))

    # Then
    assert requested_dates == [date(2015, 1, 1)]


def whenUpdateFit_thenKeepsLastDateWhenUntilIsGiven(monkeypatch):
    # Given
    mongo.configuration_collection.insert_one({"lastDate": "2026-11-20"})
    requested_ranges = []

    def fake_fetch_from_date(client, start_date, until=None):
        requested_ranges.append((start_date, until))
        return []

    monkeypatch.setattr(activity, "login", lambda interactive: "client")
    monkeypatch.setattr(activity, "fetch_from_date", fake_fetch_from_date)

    # When
    activity.update_fit(since=date(2015, 1, 1), until=date(2025, 12, 31))

    # Then
    assert requested_ranges == [(date(2015, 1, 1), date(2025, 12, 31))]
    assert mongo.get_last_date() == date(2026, 11, 20)


def whenUpdateFit_thenWaitsBetweenDownloadsButNotAfterTheLast(monkeypatch):
    # Given
    sleeps = []
    monkeypatch.setattr(activity, "login", lambda interactive: "client")
    monkeypatch.setattr(activity, "fetch_from_date",
                        lambda client, start_date, until=None: [{"activityId": 1}, {"activityId": 2}, {"activityId": 3}])
    monkeypatch.setattr(activity, "download_fit_from_id", lambda client, activity_id: {"activityId": activity_id})
    monkeypatch.setattr(activity.time, "sleep", sleeps.append)

    # When
    activity.update_fit(delay=1.5)

    # Then
    assert sleeps == [1.5, 1.5]


def whenUpdateFit_thenLogsInOnceForAllActivities(monkeypatch):
    # Given
    logins = []
    clients_used = []
    client = object()

    def fake_login(interactive):
        logins.append(interactive)
        return client

    def fake_download_fit_from_id(used_client, activity_id):
        clients_used.append(used_client)
        return {"activityId": activity_id}

    monkeypatch.setattr(activity, "login", fake_login)
    monkeypatch.setattr(activity, "fetch_from_date",
                        lambda used_client, start_date, until=None: [{"activityId": 1}, {"activityId": 2}, {"activityId": 3}])
    monkeypatch.setattr(activity, "download_fit_from_id", fake_download_fit_from_id)

    # When
    activity.update_fit()

    # Then
    assert logins == [False]
    assert clients_used == [client, client, client]
