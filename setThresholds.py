"""Stores heart-rate thresholds for hrTSS. Edit the list, then run this script. It writes to Atlas.

Each entry applies from its date until the next one. Runs before the first entry use it.

TRIMP coefficients (Banister), pick one published set:
    trimpA 0.64, trimpB 1.92
    trimpA 0.86, trimpB 1.67
"""
from mongo import upsert_threshold

threshold_list = [
    {
        "date": "2025-01-01",
        "lthr": None,
        "restingHr": None,
        "maxHr": None,
        "trimpA": None,
        "trimpB": None,
    },
]


if __name__ == "__main__":
    for threshold in threshold_list:
        missing = [key for key, value in threshold.items() if value is None]
        if missing:
            raise SystemExit(f"Fill in {', '.join(missing)} for {threshold['date']} first.")
    for threshold in threshold_list:
        upsert_threshold(threshold)
    print(f"{len(threshold_list)} threshold(s) stored.")
