from datetime import date, datetime
import zipfile
import io
import os
from dotenv import load_dotenv

from garmin_fit_sdk import Decoder, Stream
from garminconnect import Garmin, GarminConnectAuthenticationError

load_dotenv()

TOKEN_DIR = "./ressources/token"


class GarminLoginRequired(Exception):
    """Garmin needs an MFA code, but no terminal can prompt for it."""


def login(interactive: bool) -> Garmin:
    """Logs in to Garmin Connect.

    Uses the saved tokens. Falls back to email/password only if they are
    missing or rejected.

    Args:
        interactive: Whether to prompt for an MFA code on stdin.

    Returns:
        A logged-in Garmin client.

    Raises:
        GarminLoginRequired: An MFA code is needed and interactive is False.
    """
    try:
        return __login_with_tokens()
    except (FileNotFoundError, GarminConnectAuthenticationError):
        pass

    garmin = Garmin(email=os.getenv("GARMIN_MAIL"), password=os.getenv(
        "GARMIN_PASSWORD"), return_on_mfa=True)
    result1, result2 = garmin.login()
    if result1 == "needs_mfa":
        if not interactive:
            raise GarminLoginRequired(
                "Garmin needs an MFA code. Run in a terminal: .venv/Scripts/python.exe activity.py")
        mfa_code = input("MFA one-time code (via email or SMS): ")
        garmin.resume_login(result2, mfa_code)
    garmin.garth.dump(TOKEN_DIR)
    # The MFA login path skips loading the profile, so reload from the tokens.
    return __login_with_tokens()


def __login_with_tokens() -> Garmin:
    garmin = Garmin()
    garmin.login(TOKEN_DIR)
    return garmin


def download_fit_from_id(client: Garmin, activity_id: str) -> dict[str, any]:
    """Downloads an activity's FIT file and reads its workout feel and RPE."""
    with zipfile.ZipFile(io.BytesIO(__fetch_fit_from_id(client, activity_id)), 'r') as zip_ref:
        filenames = zip_ref.namelist()
        file_data = zip_ref.read(filenames[0])

    bytearray_data = bytearray(file_data)

    stream = Stream.from_byte_array(byte_array=bytearray_data)
    return __read_running_fit_data_stream(activity_id, stream)


def fetch_from_date(client: Garmin, date: date, until: date | None = None) -> None:
    """Fetches activities from a date, up to `until` if given. Parses their times to datetimes."""
    activity_list = client.get_activities_by_date(
        startdate=date.isoformat(), enddate=until.isoformat() if until else None)
    for activity in activity_list:
        activity['startTimeLocal'] = datetime.strptime(
            activity['startTimeLocal'], "%Y-%m-%d %H:%M:%S")
        activity['startTimeGMT'] = datetime.strptime(
            activity['startTimeGMT'], "%Y-%m-%d %H:%M:%S")
        activity['endTimeGMT'] = datetime.strptime(
            activity['endTimeGMT'], "%Y-%m-%d %H:%M:%S")
    return activity_list


def __fetch_fit_from_id(client: Garmin, id: str) -> None:
    return client.download_activity(activity_id=id, dl_fmt=Garmin.ActivityDownloadFormat.ORIGINAL)


def __read_running_fit_data_stream(activity_id: str, fit_stream: Stream) -> dict[str, any]:
    decoder = Decoder(fit_stream)
    messages, _ = decoder.read()

    session_mesgs = [entry for entry in messages['session_mesgs']][0]

    workout_feel = session_mesgs.get('workout_feel')
    workout_rpe = session_mesgs.get('workout_rpe')

    return {
        'activityId': activity_id,
        'workoutFeel': workout_feel,
        'workoutRpe': workout_rpe,
    }
