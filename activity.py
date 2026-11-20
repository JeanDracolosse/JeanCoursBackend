from garmin import download_fit_from_id, fetch_from_date, login
from mongo import get_last_date, set_last_date, upsert_activity


def update_fit(interactive: bool = False) -> None:
    client = login(interactive)
    last_date = get_last_date()
    activity_list = fetch_from_date(client, last_date)
    for activity in activity_list:
        upsert_activity(activity)
        fit_activity = download_fit_from_id(client, activity['activityId'])
        upsert_activity(fit_activity)
    set_last_date()

if __name__ == "__main__":
    update_fit(interactive=True)
