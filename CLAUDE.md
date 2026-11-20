# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Python FastAPI backend that syncs running activities from Garmin Connect into MongoDB Atlas (database `jeanCours`) and exposes weekly training statistics (HR/power time in zone, distance, arbitrary metrics) for a frontend. Despite the folder name (`Projets/Javascript`), this repo is Python only.

## Commands

Use the project virtualenv at `.venv` (Windows layout):

```sh
.venv/Scripts/python.exe -m pip install -r requirements.txt   # install deps
.venv/Scripts/python.exe main.py                              # run API on 0.0.0.0:8000
.venv/Scripts/python.exe -m uvicorn main:app --reload         # run API with autoreload
.venv/Scripts/python.exe activity.py                          # sync Garmin -> Mongo (same as GET /garmin)
.venv/Scripts/python.exe setWeekData.py                       # seed week types + upsert one week (edit the dict first)
```

There is no test suite, linter, or formatter configured.

## Configuration

`.env` (gitignored) must define `MONGO_USERNAME`, `MONGO_PASSWORD`, `MONGO_URL`, `MONGO_APP_NAME`, `GARMIN_MAIL`, `GARMIN_PASSWORD`. Garmin session tokens are cached in `ressources/token` (sensitive; must not be committed). If the token is missing or invalid, `garmin.py` falls back to email/password login and may prompt on stdin for an MFA code, so the first sync must run interactively.

## Architecture

Layering: `main.py` (routes) → `mongo.py` (data access) → `aggregation.py` (pipeline definitions). Sync path: `activity.py` → `garmin.py` + `mongo.py`.

- **Import-time side effects:** importing `mongo.py` connects to Atlas and creates collections/unique indexes (`activities.activityId`, `weekTypes.weekTypeId`, `weeks.date`). Any module importing it (including `main.py`) needs a reachable DB.
- **Sync (`update_fit`):** reads `configuration.lastDate` (defaults to today), fetches activities since then, upserts each Garmin summary, then downloads the original FIT file and merges `workoutFeel`/`workoutRpe` into the same document, then sets `lastDate` to today. Activities are stored as the raw Garmin JSON (camelCase fields like `distance`, `hrTimeInZone_1`, `startTimeLocal` converted to `datetime`).
- **Weekly aggregation contract:** every stats pipeline filters `activityType.typeId in [1, 6]` (running types), buckets by ISO year/week of `startTimeLocal`, sorts by the week key, then collapses to a single document of **parallel arrays** (one entry per week). `/index` returns the matching list of week start dates that serves as the x-axis. Arrays from different endpoints line up only because they use the same filter and sort, so keep them consistent when changing a pipeline.
- **Week key gotchas:** the `_id` key is a string `"{year}_{week}"` (or `"{year}-{week}"` in `INDEX_PIPELINE`), so the `$sort` is lexicographic (`2025_10` sorts before `2025_9`), not chronological. `get_indexes` parses the ISO week with `%W`, which is not ISO week numbering.
- **Dynamic metrics:** `/metricsAvgByWeek`, `/metricsSumByWeek` and `/metricsByActivity` take a repeated `metrics` query param of raw activity field names and build `$avg`/`$sum`/`$push` stages from them.
- **Week planning:** the `weeks` collection (`date`, `weekTypeId`) is joined with `weekTypes` (`weekTypeId`, `label`: Base/Récupération/Intensive/Spécifique) by `/weekTypes`. It is populated manually through `setWeekData.py`.
- In `main.py`, several handlers share the same Python function name (`root`, `get_metrics`). FastAPI still registers each route, but give new handlers unique names.
