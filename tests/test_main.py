import pytest
from fastapi.testclient import TestClient

import main
import mongo
from garmin import GarminLoginRequired


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


def whenGetDistanceRoute_thenAcceptsFromAndTo(client, two_weeks_of_runs):
    # Given
    # When
    response = client.get("/distance", params={"from": "2025-03-10", "to": "2025-03-16"})

    # Then
    assert response.status_code == 200
    assert response.json()["distance"] == [8000]


def whenGetDistanceRoute_thenRejectsFromAfterTo(client):
    # Given
    # When
    response = client.get("/distance", params={"from": "2025-03-16", "to": "2025-03-10"})

    # Then
    assert response.status_code == 422


def whenGetDistanceRoute_thenAcceptsActivityTypes(client, two_weeks_of_runs):
    # Given
    # When
    response = client.get("/distance", params={"types": [2]})

    # Then
    assert response.status_code == 200
    assert response.json()["distance"] == [40000]


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
    assert response.json() == {"distance": [15000, 8000], "elevationGain": [100, 20]}


def whenGetMetricsAvgByWeekRoute_thenAveragesEveryRequestedMetric(client, two_weeks_of_runs):
    # Given
    # When
    response = client.get("/metricsAvgByWeek", params={"metrics": ["averageHR"]})

    # Then
    assert response.status_code == 200
    assert response.json() == {"averageHR": [145, 160]}


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
        "distance": [10000, 5000],
        "startTimeLocal": ["2025-03-03T08:00:00", "2025-03-05T18:00:00"],
    }


def whenGetMetricsByActivityRoute_thenReturnsEmptyArraysForWeekWithoutRuns(client, two_weeks_of_runs):
    # Given
    # When
    response = client.get("/metricsByActivity", params={"year": 2025, "week": 30, "metrics": ["distance"]})

    # Then
    assert response.status_code == 200
    assert response.json() == {"distance": [], "startTimeLocal": []}


def whenGetDistanceRoute_thenReturnsEmptyArraysWithoutRuns(client):
    # Given
    # When
    response = client.get("/distance")

    # Then
    assert response.status_code == 200
    assert response.json()["distance"] == []


def whenGetMetricsByActivityRoute_thenRejectsRequestWithoutMetrics(client):
    # Given
    # When
    response = client.get("/metricsByActivity", params={"year": 2025, "week": 10})

    # Then
    assert response.status_code == 422


def whenGetMetricsByActivityRoute_thenRejectsRequestWithoutWeek(client):
    # Given
    # When
    response = client.get("/metricsByActivity", params={"year": 2025, "metrics": ["distance"]})

    # Then
    assert response.status_code == 422


def whenGetOpenApi_thenDocumentsEveryRouteWithSchemas(client):
    # Given
    # When
    response = client.get("/openapi.json")

    # Then
    assert response.status_code == 200
    spec = response.json()
    assert set(spec["paths"]) == {"/index", "/distance", "/hrTimeInZone", "/powerTimeInZone", "/metricsSumByWeek",
                                  "/metricsAvgByWeek", "/metricsByActivity", "/weekTypes", "/garmin"}
    assert "DistanceWeeks" in spec["components"]["schemas"]


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


def whenGetGarminRoute_thenReturns401WhenLoginNeedsMfa(client, monkeypatch):
    # Given
    def sync_needing_mfa():
        raise GarminLoginRequired("Garmin needs an MFA code. Run in a terminal: .venv/Scripts/python.exe activity.py")

    monkeypatch.setattr(main, "update_fit", sync_needing_mfa)

    # When
    response = client.get("/garmin")

    # Then
    assert response.status_code == 401
    assert "activity.py" in response.json()["detail"]
