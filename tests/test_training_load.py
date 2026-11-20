from datetime import date

import pytest

from jean_cours.stats.training_load import Threshold, daily_load, hr_tss, threshold_on

THRESHOLD = Threshold(date(2025, 1, 1), lthr=170, resting_hr=50, max_hr=190, trimp_a=0.64, trimp_b=1.92)


def whenHrTss_thenScoresOneHourAtLthrAs100():
    # Given
    # When
    result = hr_tss(3600, 170, THRESHOLD)

    # Then
    assert result == pytest.approx(100)


def whenHrTss_thenScoresAnEasierHourBelow100():
    # Given
    # When
    result = hr_tss(3600, 140, THRESHOLD)

    # Then
    assert 0 < result < 100


def whenHrTss_thenClampsHeartRateAboveMax():
    # Given
    # When
    above_max = hr_tss(3600, 200, THRESHOLD)

    # Then
    assert above_max == pytest.approx(hr_tss(3600, 190, THRESHOLD))


def whenHrTss_thenScoresZeroWithoutHeartRateOrDuration():
    # Given
    # When
    without_hr = hr_tss(3600, None, THRESHOLD)
    without_duration = hr_tss(None, 150, THRESHOLD)

    # Then
    assert without_hr == 0
    assert without_duration == 0


def whenDailyLoad_thenAddsOneDayOfTssToCtlAndAtl():
    # Given
    day = date(2025, 3, 3)

    # When
    result = daily_load({day: 100}, day, day)

    # Then
    assert result["ctl"] == [pytest.approx(100 / 42)]
    assert result["atl"] == [pytest.approx(100 / 7)]
    assert result["tsb"] == [0]


def whenDailyLoad_thenTsbUsesThePreviousDay():
    # Given
    first, second = date(2025, 3, 3), date(2025, 3, 4)

    # When
    result = daily_load({first: 100, second: 50}, first, second)

    # Then
    assert result["tsb"][1] == pytest.approx(result["ctl"][0] - result["atl"][0])


def whenDailyLoad_thenRestDaysDecayCtlAndAtl():
    # Given
    first, second = date(2025, 3, 3), date(2025, 3, 4)

    # When
    result = daily_load({first: 100}, first, second)

    # Then
    assert result["date"] == [first, second]
    assert result["tss"] == [100, 0]
    assert result["ctl"][1] == pytest.approx(result["ctl"][0] * 41 / 42)
    assert result["atl"][1] == pytest.approx(result["atl"][0] * 6 / 7)


def whenThresholdOn_thenPicksTheLatestThresholdOnOrBeforeTheDay():
    # Given
    spring = Threshold(date(2025, 4, 1), lthr=172, resting_hr=48, max_hr=190, trimp_a=0.64, trimp_b=1.92)
    thresholds = [THRESHOLD, spring]

    # When
    in_march = threshold_on(date(2025, 3, 31), thresholds)
    in_april = threshold_on(date(2025, 4, 1), thresholds)

    # Then
    assert in_march == THRESHOLD
    assert in_april == spring


def whenThresholdOn_thenUsesTheFirstThresholdBeforeAnyThreshold():
    # Given
    # When
    result = threshold_on(date(2024, 6, 1), [THRESHOLD])

    # Then
    assert result == THRESHOLD
