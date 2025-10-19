from datetime import date, datetime
import zipfile
import io
import os
from dotenv import load_dotenv

from garmin_fit_sdk import Decoder, Stream
from garminconnect import Garmin

load_dotenv()

TOKEN_DIR = "./ressources/token"


def __garmin() -> Garmin:
    try:
        garmin = Garmin()
        garmin.login(TOKEN_DIR)
        return garmin
    except:
        garmin = Garmin(email=os.getenv("GARMIN_MAIL"), password=os.getenv(
            "GARMIN_PASSWORD"), return_on_mfa=True)
        result1, result2 = garmin.login()
        if result1 == "needs_mfa":
            mfa_code = input("MFA one-time code (via email or SMS): ")
            garmin.resume_login(result2, mfa_code)
        garmin.garth.dump(TOKEN_DIR)
        return __garmin()


def download_fit_from_id(activity_id: str) -> dict[str, any]:
    with zipfile.ZipFile(io.BytesIO(__fetch_fit_from_id(activity_id)), 'r') as zip_ref:
        filenames = zip_ref.namelist()
        file_data = zip_ref.read(filenames[0])

    bytearray_data = bytearray(file_data)

    stream = Stream.from_byte_array(byte_array=bytearray_data)
    return __read_running_fit_data_stream(activity_id, stream)


def fetch_from_date(date: date) -> None:
    activity_list = __garmin().get_activities_by_date(startdate=date.isoformat())
    for activity in activity_list:
        activity['startTimeLocal'] = datetime.strptime(
            activity['startTimeLocal'], "%Y-%m-%d %H:%M:%S")
        activity['startTimeGMT'] = datetime.strptime(
            activity['startTimeGMT'], "%Y-%m-%d %H:%M:%S")
        activity['endTimeGMT'] = datetime.strptime(
            activity['endTimeGMT'], "%Y-%m-%d %H:%M:%S")
    return activity_list


def __fetch_fit_from_id(id: str) -> None:
    return __garmin().download_activity(activity_id=id, dl_fmt=Garmin.ActivityDownloadFormat.ORIGINAL)


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