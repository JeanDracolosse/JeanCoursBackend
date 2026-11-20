import argparse
import time
from datetime import date

from garmin import download_fit_from_id, fetch_from_date, login
from mongo import get_last_date, set_last_date, upsert_activity


def update_fit(interactive: bool = False, since: date | None = None, until: date | None = None,
               delay: float = 0) -> None:
    """Syncs activities from Garmin.

    Args:
        interactive: Whether a terminal can prompt for an MFA code and show progress.
        since: Fetch from this date instead of the last sync. Used to backfill history.
        until: Fetch up to this date. A run with `until` doesn't move the last sync date.
        delay: Seconds to wait between FIT downloads, to avoid Garmin rate limits.
    """
    client = login(interactive)
    activity_list = fetch_from_date(client, since or get_last_date(), until)
    for count, activity in enumerate(activity_list, start=1):
        upsert_activity(activity)
        fit_activity = download_fit_from_id(client, activity['activityId'])
        upsert_activity(fit_activity)
        if interactive:
            print(f"{count}/{len(activity_list)} activities synced", flush=True)
        if delay and count < len(activity_list):
            time.sleep(delay)
    if until is None:
        set_last_date()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync activities from Garmin. Re-runs are safe.")
    parser.add_argument("--since", type=date.fromisoformat, help="Fetch from this date (YYYY-MM-DD) instead of the last sync.")
    parser.add_argument("--until", type=date.fromisoformat, help="Fetch up to this date (YYYY-MM-DD). Keeps the last sync date.")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between FIT downloads (default: 1).")
    arguments = parser.parse_args()
    update_fit(interactive=True, since=arguments.since, until=arguments.until, delay=arguments.delay)
