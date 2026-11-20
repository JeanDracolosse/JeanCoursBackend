import argparse
from datetime import date

from garmin import download_fit_from_id, fetch_from_date, login
from mongo import get_last_date, set_last_date, upsert_activity


def update_fit(interactive: bool = False, since: date | None = None) -> None:
    """Syncs activities from Garmin.

    Args:
        interactive: Whether a terminal can prompt for an MFA code and show progress.
        since: Fetch from this date instead of the last sync. Used to backfill history.
    """
    client = login(interactive)
    activity_list = fetch_from_date(client, since or get_last_date())
    for count, activity in enumerate(activity_list, start=1):
        upsert_activity(activity)
        fit_activity = download_fit_from_id(client, activity['activityId'])
        upsert_activity(fit_activity)
        if interactive:
            print(f"{count}/{len(activity_list)} activities synced")
    set_last_date()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync activities from Garmin.")
    parser.add_argument("--since", type=date.fromisoformat,
                        help="Fetch from this date (YYYY-MM-DD) instead of the last sync. Re-runs are safe.")
    update_fit(interactive=True, since=parser.parse_args().since)
