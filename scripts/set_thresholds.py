"""Stores the heart-rate thresholds from .env for hrTSS. It writes to Atlas.

Run from the project root: python -m scripts.set_thresholds

The threshold applies from THRESHOLD_DATE until a later one. Runs before it use it too.
Re-running with a new THRESHOLD_DATE adds a threshold; the same date updates it.

.env keys: THRESHOLD_DATE (YYYY-MM-DD), LTHR, RESTING_HR, MAX_HR, TRIMP_A, TRIMP_B.
TRIMP coefficients (Banister), one published set:
    TRIMP_A 0.64, TRIMP_B 1.92
    TRIMP_A 0.86, TRIMP_B 1.67
"""
import os
from datetime import date

from dotenv import load_dotenv

from jean_cours.db import upsert_threshold

load_dotenv()

KEYS = ["THRESHOLD_DATE", "LTHR", "RESTING_HR", "MAX_HR", "TRIMP_A", "TRIMP_B"]


def read_threshold() -> dict:
    """Reads the threshold from the environment.

    Raises:
        SystemExit: A key is missing.
    """
    missing = [key for key in KEYS if not os.getenv(key)]
    if missing:
        raise SystemExit(f"Set {', '.join(missing)} in .env first.")
    return {
        "date": date.fromisoformat(os.getenv("THRESHOLD_DATE")).isoformat(),
        "lthr": float(os.getenv("LTHR")),
        "restingHr": float(os.getenv("RESTING_HR")),
        "maxHr": float(os.getenv("MAX_HR")),
        "trimpA": float(os.getenv("TRIMP_A")),
        "trimpB": float(os.getenv("TRIMP_B")),
    }


if __name__ == "__main__":
    threshold = read_threshold()
    upsert_threshold(threshold)
    print(f"Threshold from {threshold['date']} stored.")
