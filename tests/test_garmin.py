import io
import zipfile
from datetime import datetime
from types import SimpleNamespace

import pytest
from garminconnect import Garmin, GarminConnectAuthenticationError, GarminConnectConnectionError

import garmin


@pytest.fixture
def fake_garmin(monkeypatch):
    """Fakes the Garmin class and records logins in FakeGarmin.calls.

    Set token_login_errors and needs_mfa to pick a scenario.
    """
    calls = []

    class FakeGarmin:
        ActivityDownloadFormat = Garmin.ActivityDownloadFormat
        token_login_errors = []
        needs_mfa = False

        def __init__(self, email=None, password=None, return_on_mfa=False):
            self.garth = SimpleNamespace(dump=lambda path: calls.append(("dump tokens", path)))

        def login(self, tokenstore=None):
            if tokenstore:
                calls.append("token login")
                if FakeGarmin.token_login_errors:
                    raise FakeGarmin.token_login_errors.pop(0)
                return None, None
            calls.append("password login")
            return ("needs_mfa", "mfa-state") if FakeGarmin.needs_mfa else (None, None)

        def resume_login(self, client_state, mfa_code):
            calls.append(("resume login", client_state, mfa_code))

    FakeGarmin.calls = calls
    monkeypatch.setattr(garmin, "Garmin", FakeGarmin)
    return FakeGarmin


@pytest.fixture
def no_terminal(monkeypatch):
    def fail_if_prompted(prompt=""):
        raise AssertionError("input() must not be called")
    monkeypatch.setattr("builtins.input", fail_if_prompted)


def whenLogin_thenUsesSavedTokensWithoutPassword(fake_garmin):
    # Given
    # When
    client = garmin.login(interactive=False)

    # Then
    assert isinstance(client, fake_garmin)
    assert fake_garmin.calls == ["token login"]


def whenLogin_thenFallsBackToPasswordWhenTokensAreMissing(fake_garmin):
    # Given
    fake_garmin.token_login_errors = [FileNotFoundError("no token dir")]

    # When
    garmin.login(interactive=False)

    # Then
    assert fake_garmin.calls == ["token login", "password login", ("dump tokens", garmin.TOKEN_DIR), "token login"]


def whenLogin_thenFallsBackToPasswordWhenTokensAreRejected(fake_garmin):
    # Given
    fake_garmin.token_login_errors = [GarminConnectAuthenticationError("token expired")]

    # When
    garmin.login(interactive=False)

    # Then
    assert fake_garmin.calls == ["token login", "password login", ("dump tokens", garmin.TOKEN_DIR), "token login"]


def whenLogin_thenDoesNotUsePasswordOnConnectionError(fake_garmin):
    # Given
    fake_garmin.token_login_errors = [GarminConnectConnectionError("network down")]

    # When
    with pytest.raises(GarminConnectConnectionError):
        garmin.login(interactive=False)

    # Then
    assert fake_garmin.calls == ["token login"]


def whenLogin_thenRaisesLoginRequiredWhenMfaNeededAndNotInteractive(fake_garmin, no_terminal):
    # Given
    fake_garmin.token_login_errors = [GarminConnectAuthenticationError("token expired")]
    fake_garmin.needs_mfa = True

    # When
    with pytest.raises(garmin.GarminLoginRequired, match="activity.py"):
        garmin.login(interactive=False)

    # Then
    assert fake_garmin.calls == ["token login", "password login"]


def whenLogin_thenPromptsForMfaWhenInteractive(fake_garmin, monkeypatch):
    # Given
    fake_garmin.token_login_errors = [GarminConnectAuthenticationError("token expired")]
    fake_garmin.needs_mfa = True
    monkeypatch.setattr("builtins.input", lambda prompt="": "123456")

    # When
    garmin.login(interactive=True)

    # Then
    assert fake_garmin.calls == [
        "token login",
        "password login",
        ("resume login", "mfa-state", "123456"),
        ("dump tokens", garmin.TOKEN_DIR),
        "token login",
    ]


class _FakeClient:
    def __init__(self, fit_content=b""):
        self.fit_content = fit_content
        self.downloaded_ids = []

    def get_activities_by_date(self, startdate):
        return [{
            "activityId": 1,
            "startTimeLocal": "2025-03-03 08:00:00",
            "startTimeGMT": "2025-03-03 07:00:00",
            "endTimeGMT": "2025-03-03 08:00:00",
        }]

    def download_activity(self, activity_id, dl_fmt):
        self.downloaded_ids.append(activity_id)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zip_file:
            zip_file.writestr("activity.fit", self.fit_content)
        return buffer.getvalue()


class _FakeDecoder:
    def __init__(self, stream):
        pass

    def read(self):
        return {"session_mesgs": [{"workout_feel": 50, "workout_rpe": 30}]}, []


def whenFetchFromDate_thenParsesActivityTimesIntoDatetimes():
    # Given
    client = _FakeClient()

    # When
    result = garmin.fetch_from_date(client, datetime(2025, 3, 1).date())

    # Then
    assert result == [{
        "activityId": 1,
        "startTimeLocal": datetime(2025, 3, 3, 8),
        "startTimeGMT": datetime(2025, 3, 3, 7),
        "endTimeGMT": datetime(2025, 3, 3, 8),
    }]


def whenDownloadFitFromId_thenReturnsWorkoutFeelAndRpe(monkeypatch):
    # Given
    client = _FakeClient(fit_content=b"fit-bytes")
    monkeypatch.setattr(garmin, "Decoder", _FakeDecoder)

    # When
    result = garmin.download_fit_from_id(client, "42")

    # Then
    assert result == {"activityId": "42", "workoutFeel": 50, "workoutRpe": 30}
    assert client.downloaded_ids == ["42"]
