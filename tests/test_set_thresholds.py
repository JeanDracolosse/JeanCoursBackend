import pytest

from scripts import set_thresholds

ENV = {"THRESHOLD_DATE": "2025-01-01", "LTHR": "170", "RESTING_HR": "50", "MAX_HR": "190",
       "TRIMP_A": "0.64", "TRIMP_B": "1.92"}


def whenReadThreshold_thenBuildsTheThresholdFromTheEnvironment(monkeypatch):
    # Given
    for key, value in ENV.items():
        monkeypatch.setenv(key, value)

    # When
    result = set_thresholds.read_threshold()

    # Then
    assert result == {"date": "2025-01-01", "lthr": 170, "restingHr": 50, "maxHr": 190, "trimpA": 0.64, "trimpB": 1.92}


def whenReadThreshold_thenStopsWhenAKeyIsMissing(monkeypatch):
    # Given
    for key, value in ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("MAX_HR")

    # When
    with pytest.raises(SystemExit, match="MAX_HR"):
        set_thresholds.read_threshold()

    # Then
