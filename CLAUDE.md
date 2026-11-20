# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Python backend for running stats. A FastAPI web API, **exposed on the web**, serves weekly and daily training statistics (distance, HR/power zones, any Garmin metric, hrTSS/CTL/ATL/TSB) from MongoDB Atlas (database `jeanCours`) to a frontend. A separate sync, run locally, fills Atlas from Garmin Connect. Despite the folder name (`Projets/Javascript`), this repo is Python only.

## Commands

Use the project virtualenv at `.venv` (Windows layout, Python 3.15). Run everything from the project root. To recreate it: `py -3.15 -m venv .venv`, then install `requirements-dev.txt`. When upgrading, pick versions that support the venv's Python and were released at least two weeks ago; install with `--only-binary=:all:` to catch missing wheels.

```sh
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt   # everything: web + sync + tests + uvicorn
.venv/Scripts/python.exe -m jean_cours                            # run the API on 0.0.0.0:8000
.venv/Scripts/python.exe -m uvicorn jean_cours.api.app:app --reload   # run the API with autoreload
.venv/Scripts/python.exe -m pytest                                # run all tests
.venv/Scripts/python.exe -m pytest tests/test_weekly.py::whenGetDistance_thenSumsDistanceAndEffortPerWeekForRunsOnly   # one test
.venv/Scripts/python.exe -m pytest -k Distance                    # tests matching a name
```

Scripts below touch Atlas and/or Garmin. **Ask the user before running any of them**, and before anything else that imports `jean_cours.db` outside the tests.

```sh
.venv/Scripts/python.exe -m scripts.sync_garmin                   # sync Garmin -> Atlas since the last sync
.venv/Scripts/python.exe -m scripts.sync_garmin --since 2015-01-01 --until 2024-12-31   # backfill a period (re-runs are safe; --until keeps the last sync date)
# --delay N: seconds between FIT downloads (default 1) to avoid Garmin rate limits.
.venv/Scripts/python.exe -m scripts.set_week_data                 # seed week types + upsert one week (edit the dict first)
.venv/Scripts/python.exe -m scripts.set_thresholds                # store the HR threshold from .env for hrTSS
```

No linter or formatter is configured.

## Layout

```
jean_cours/          web API package (deployed). Never imports Garmin code.
  __main__.py        runs uvicorn
  db.py              Mongo connection (on import), collections, upserts, last sync date
  api/app.py         FastAPI routes; api/schemas.py response models (Swagger)
  stats/pipelines.py Mongo pipeline builders, ActivityFilter, field specs
  stats/weekly.py    stats queries (weekly arrays, per-activity, training load)
  stats/training_load.py  pure hrTSS / CTL / ATL / TSB math
garmin_sync/         Garmin client (client.py) and sync (sync.py). Local only.
scripts/             CLI entry points, run with python -m scripts.<name>
docs/                garmin-activity-fields.md: activity fields with units
```

- **Boundary:** `jean_cours/` must never import `garmin_sync`, `garminconnect` or `garmin_fit_sdk`. `tests/test_architecture.py` enforces it. Garmin credentials and tokens are only needed where the sync runs, not on the web server. There is no sync route.
- **Requirements:** `requirements.txt` is what the web API needs at runtime and is all that Vercel installs, so keep Garmin and dev packages out of it. `requirements-sync.txt` adds the Garmin packages; `requirements-dev.txt` adds uvicorn and the test tools.

## Deployment

Vercel deploys from GitHub `main` (pushing deploys). `pyproject.toml` only sets `[tool.vercel] entrypoint = "jean_cours.api.app:app"`; dependencies come from `requirements.txt`. Vercel offers Python 3.12 (default), 3.13 and 3.14, not 3.15, so `.python-version` pins 3.14. Dependency upgrades must also have wheels for that version (check with `pip install --dry-run --python-version 3.14 --only-binary=:all: --platform manylinux_2_17_x86_64 --implementation cp --target <tmp> -r requirements.txt`). Mongo credentials are Vercel environment variables, not `.env`.

## Comments

Google-style docstrings (`Args:`, `Returns:`, `Raises:`). Comment only when the code doesn't say it already. Keep it minimal, in short sentences.

## Tests

- Naming: test functions are `whenMethodName_thenWhatItDoes` (`pytest.ini` collects `when*`, not `test_*`). Each test body has three sections marked `# Given`, `# When`, `# Then`; keep the comments even when a section is empty.
- `tests/conftest.py` replaces `pymongo.MongoClient` with an in-memory mongomock client **before** `jean_cours.db` is imported, and empties all collections before each test. Tests never touch Atlas. Never import app modules in `conftest.py` above that patch.
- mongomock lacks `$isoWeek`/`$isoWeekYear`; `conftest.py` patches them in. It also patches `$group` to return no document on empty input, like real MongoDB (mongomock returns one, which hides empty-result bugs). If a new pipeline uses another unsupported operator, mongomock raises `NotImplementedError`, so patch it there the same way.
- Garmin is never called: tests `monkeypatch` the names imported into `garmin_sync.sync` (`login`, `fetch_from_date`, `download_fit_from_id`), replace `garmin_sync.client.Garmin` with the `fake_garmin` fixture in `tests/test_garmin_client.py`, or pass a fake client object to `fetch_from_date` / `download_fit_from_id`. Because Garmin is faked, a garminconnect upgrade is only proven by a real sync.
- Pin a known bug with a `@pytest.mark.xfail(strict=True)` test. Fixing the bug makes the test pass, which fails the run until the `xfail` marker is removed.

## Configuration

`.env` (gitignored) must define `MONGO_USERNAME`, `MONGO_PASSWORD`, `MONGO_URL`, `MONGO_APP_NAME`; for the sync `GARMIN_MAIL`, `GARMIN_PASSWORD`; for `set_thresholds` `THRESHOLD_DATE`, `LTHR`, `RESTING_HR`, `MAX_HR`, `TRIMP_A`, `TRIMP_B`. Keep personal values (thresholds included) in `.env`, never in committed files.

Garmin tokens are cached in `ressources/token/garmin_tokens.json` (garminconnect 0.3 native format; sensitive; gitignored). The library refreshes them itself. Only when they are missing or rejected (`GarminConnectAuthenticationError`) does `garmin_sync.client.login` fall back to email/password. Network and rate-limit errors propagate and never trigger a password login. If Garmin then asks for an MFA code, only an interactive run (`scripts.sync_garmin`) prompts; a non-interactive call raises `GarminLoginRequired`.

## Architecture

Layering: `api/app.py` (routes) → `stats/weekly.py` (queries) → `stats/pipelines.py` (pipeline builders) + `db.py` (collections). Sync path: `scripts/sync_garmin.py` → `garmin_sync/sync.py` → `garmin_sync/client.py` + `jean_cours/db.py`.

- **Swagger:** generated by FastAPI at `/docs` (spec at `/openapi.json`). Every route declares `response_model`, `tags` and `summary`; response models live in `api/schemas.py`, with units in field descriptions. A new route or metric needs the same. FastAPI validates responses against these models, so a mismatch is a 500.
- **Import-time side effects:** importing `jean_cours.db` connects to Atlas and ensures unique indexes (`activities.activityId`, `weekTypes.weekTypeId`, `weeks.date`, `thresholds.date`). Anything importing it needs a reachable DB.
- **Sync (`update_fit`):** logs in once and passes that client to every Garmin call. It reads `configuration.lastDate` (defaults to today) unless `since` is given, fetches activities (garminconnect pages through them), upserts each Garmin summary, then downloads the original FIT file and merges `workoutFeel`/`workoutRpe` into the same document. Then it sets `lastDate` to today, unless `until` is given. Activities are stored as the raw Garmin JSON (camelCase fields like `distance`, `hrTimeInZone_1`, `startTimeLocal` converted to `datetime`).
- **Weekly aggregation contract:** weekly endpoints return **parallel arrays**, one value per ISO week, aligned with `/index` (the Monday of each week, the x-axis). Every week in the range is present: weeks without runs are `0` for sums and `null` for averages.
  - `pipelines.weekly_pipeline(activity_filter, fields, accumulator)` returns one Mongo document per week with runs, grouped on `WEEK_GROUP_ID` (`{year, week}` numbers).
  - `weekly._weekly_arrays` builds the arrays in Python over `weekly._weeks(activity_filter)`, which is also what `get_indexes` returns. That shared week list is what keeps endpoints aligned, so new weekly endpoints must go through `_weekly_arrays`.
  - A new weekly stat is a fields dict like `DISTANCE_FIELDS` (output name → `$project` expression, `1` for a raw field), not a new pipeline.
- **Activity filter:** `pipelines.ActivityFilter(start, end, types)` selects the activities. Weekly routes get it from the `from`/`to`/`types` query params through the `Filter` dependency in `api/app.py`. Bounds are widened to whole ISO weeks. Without bounds, the range is the first to the last matching run. `types` defaults to `RUNNING_TYPES` (1, 6).
- **Dates:** when turning a week key into a date, use ISO (`date.fromisocalendar`, `%G-%V-%u`, `week_monday`), never `%Y`/`%W`.
- **Dynamic metrics:** `/metricsAvgByWeek`, `/metricsSumByWeek` and `/metricsByActivity` take a repeated `metrics` query param of raw activity field names, listed with units in `docs/garmin-activity-fields.md`. `/metricsAvgByWeek` weights each run by `duration` (`pipelines.weighted_average_fields`) and ignores runs without the metric. `/metricsByActivity` (one value per run, not per week) uses its own pipeline and returns empty arrays for a week without runs.
- **Training load:** `/trainingLoad` (weekly) and `/trainingLoadByDay`.
  - `stats/training_load.py` holds the pure math: `hr_tss` (Banister TRIMP from `duration` and `averageHR`, scaled so 1 h at LTHR = 100) and `daily_load` (CTL/ATL over 42/7 days; TSB = previous day's CTL − ATL).
  - Thresholds (`lthr`, `restingHr`, `maxHr`, `trimpA`, `trimpB`) are dated documents in `thresholds`, set by `scripts.set_thresholds` from `.env` (one dated entry per run; a new `THRESHOLD_DATE` adds one). Each run uses the latest one on or before its day. None stored → `weekly.NoThresholds` → 409.
  - CTL/ATL always start from the first matching run in all history (warm-up), then are sliced to the requested range. Weekly CTL/ATL/TSB are the week's last day's values, up to today.
- **Week planning:** the `weeks` collection (`date`, `weekTypeId`) is joined with `weekTypes` (`weekTypeId`, `label`: Base/Récupération/Intensive/Spécifique) by `/weekTypes`. It is populated manually through `scripts.set_week_data`.
