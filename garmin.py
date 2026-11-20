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
    """Garmin asked for an MFA code but no one is there to type it."""


def login(interactive: bool) -> Garmin:
    """Log in with the saved tokens, falling back to email/password only
    when the tokens are missing or rejected. Network and rate-limit errors
    are raised as-is so they never trigger a password login."""
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
    # Reload from the fresh tokens: the MFA early-return login skips loading the profile.
    return __login_with_tokens()


def __login_with_tokens() -> Garmin:
    garmin = Garmin()
    garmin.login(TOKEN_DIR)
    return garmin


def download_fit_from_id(client: Garmin, activity_id: str) -> dict[str, any]:
    with zipfile.ZipFile(io.BytesIO(__fetch_fit_from_id(client, activity_id)), 'r') as zip_ref:
        filenames = zip_ref.namelist()
        file_data = zip_ref.read(filenames[0])

    bytearray_data = bytearray(file_data)

    stream = Stream.from_byte_array(byte_array=bytearray_data)
    return __read_running_fit_data_stream(activity_id, stream)


def fetch_from_date(client: Garmin, date: date) -> None:
    activity_list = client.get_activities_by_date(startdate=date.isoformat())
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
