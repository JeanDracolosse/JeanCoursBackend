import pytest
from fastapi.testclient import TestClient

import main
import mongo


@pytest.fixture
def client():
    return TestClient(main.app)


def whenGetDistanceRoute_thenReturnsWeeklyDistance(client, two_weeks_of_runs):
    # Given
    # When
    response = client.get("/distance")

    # Then
    assert response.status_code == 200
    assert response.json()["distance"] == [15000, 8000]


def whenGetHrTimeInZoneRoute_thenReturnsWeeklyZones(client, two_weeks_of_runs):
    # Given
    # When
    response = client.get("/hrTimeInZone")

    # Then
    assert response.status_code == 200
    assert response.json()["hrTimeInZone_5"] == [350, 5]


def whenGetPowerTimeInZoneRoute_thenReturnsWeeklyZones(client, two_weeks_of_runs):
    # Given
    # When
    response = client.get("/powerTimeInZone")

    # Then
    assert response.status_code == 200
    assert response.json()["powerTimeInZone_5"] == [10, 10]


def whenGetIndexRoute_thenReturnsOneDatePerWeek(client, two_weeks_of_runs):
    # Given
    # When
    response = client.get("/index")

    # Then
    assert response.status_code == 200
    assert len(response.json()) == 2


def whenGetMetricsSumByWeekRoute_thenSumsEveryRequestedMetric(client, two_weeks_of_runs):
    # Given
    # When
    response = client.get("/metricsSumByWeek", params={"metrics": ["distance", "elevationGain"]})

    # Then
    assert response.status_code == 200
    assert response.json() == {"_id": None, "distance": [15000, 8000], "elevationGain": [100, 20]}


def whenGetMetricsAvgByWeekRoute_thenAveragesEveryRequestedMetric(client, two_weeks_of_runs):
    # Given
    # When
    response = client.get("/metricsAvgByWeek", params={"metrics": ["averageHR"]})

    # Then
    assert response.status_code == 200
    assert response.json() == {"_id": None, "averageHR": [145, 160]}


def whenGetMetricsAvgByWeekRoute_thenRejectsRequestWithoutMetrics(client):
    # Given
    # When
    response = client.get("/metricsAvgByWeek")

    # Then
    assert response.status_code == 422


def whenGetMetricsByActivityRoute_thenReturnsRunsOfThatWeek(client, two_weeks_of_runs):
    # Given
    # When
    response = client.get("/metricsByActivity", params={"year": 2025, "week": 10, "metrics": ["distance"]})

    # Then
    assert response.status_code == 200
    assert response.json() == {
        "_id": None,
        "distance": [10000, 5000],
        "startTimeLocal": ["2025-03-03T08:00:00", "2025-03-05T18:00:00"],
    }


def whenGetMetricsByActivityRoute_thenReturnsEmptyListWithoutMetrics(client, two_weeks_of_runs):
    # Given
    # When
    response = client.get("/metricsByActivity", params={"year": 2025, "week": 10})

    # Then
    assert response.status_code == 200
    assert response.json() == []


def whenGetWeekTypesRoute_thenReturnsWeeksWithLabels(client):
    # Given
    mongo.upsert_week_type({"weekTypeId": 2, "label": "Intensive"})
    mongo.upsert_week({"date": "2025-11-17", "weekTypeId": 2})

    # When
    response = client.get("/weekTypes")

    # Then
    assert response.status_code == 200
    assert response.json() == [{"date": "2025-11-17", "label": "Intensive"}]


def whenGetGarminRoute_thenRunsTheSync(client, monkeypatch):
    # Given
    calls = []
    monkeypatch.setattr(main, "update_fit", lambda: calls.append("sync"))

    # When
    response = client.get("/garmin")

    # Then
    assert response.status_code == 200
    assert calls == ["sync"]
