"""Syncs activities from Garmin. Run from the project root: python -m scripts.sync_garmin"""
import argparse
from datetime import date

from garmin_sync.sync import update_fit

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync activities from Garmin. Re-runs are safe.")
    parser.add_argument("--since", type=date.fromisoformat, help="Fetch from this date (YYYY-MM-DD) instead of the last sync.")
    parser.add_argument("--until", type=date.fromisoformat, help="Fetch up to this date (YYYY-MM-DD). Keeps the last sync date.")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between FIT downloads (default: 1).")
    arguments = parser.parse_args()
    update_fit(interactive=True, since=arguments.since, until=arguments.until, delay=arguments.delay)
