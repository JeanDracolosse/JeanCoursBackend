import io
import zipfile
from datetime import datetime

import garmin


class _FakeGarminClient:
    def get_activities_by_date(self, startdate):
        return [{
            "activityId": 1,
            "startTimeLocal": "2025-03-03 08:00:00",
            "startTimeGMT": "2025-03-03 07:00:00",
            "endTimeGMT": "2025-03-03 08:00:00",
        }]


class _FakeDecoder:
    def __init__(self, stream):
        pass

    def read(self):
        return {"session_mesgs": [{"workout_feel": 50, "workout_rpe": 30}]}, []


def _zip_containing(content: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_file:
        zip_file.writestr("activity.fit", content)
    return buffer.getvalue()


def whenFetchFromDate_thenParsesActivityTimesIntoDatetimes(monkeypatch):
    # Given
    monkeypatch.setattr(garmin, "__garmin", lambda: _FakeGarminClient())

    # When
    result = garmin.fetch_from_date(datetime(2025, 3, 1).date())

    # Then
    assert result == [{
        "activityId": 1,
        "startTimeLocal": datetime(2025, 3, 3, 8),
        "startTimeGMT": datetime(2025, 3, 3, 7),
        "endTimeGMT": datetime(2025, 3, 3, 8),
    }]


def whenDownloadFitFromId_thenReturnsWorkoutFeelAndRpe(monkeypatch):
    # Given
    monkeypatch.setattr(garmin, "__fetch_fit_from_id", lambda activity_id: _zip_containing(b"fit-bytes"))
    monkeypatch.setattr(garmin, "Decoder", _FakeDecoder)

    # When
    result = garmin.download_fit_from_id("42")

    # Then
    assert result == {"activityId": "42", "workoutFeel": 50, "workoutRpe": 30}
