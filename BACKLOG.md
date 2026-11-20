# Backlog

One topic at a time. Move an item to Done when it's committed.

## Next

- [ ] Check the Garmin login on garminconnect 0.3: tokens are now in `ressources/token/garmin_tokens.json`. The old `oauth1_token.json` / `oauth2_token.json` can be deleted once a sync works.
- [ ] **Security, API exposed on the web**: authentication, CORS limited to the frontend origin, rate limiting, a read-only Mongo user for the API

## Later

- [ ] Backfill before 2025 (optional): `python -m scripts.sync_garmin --since 2015-01-01 --until 2024-12-31`
- [ ] `groupBy=month|season` (week only for now)
- [ ] Define "season" (calendar year, race to race, or custom dates in Mongo?)

## Graph ideas

- [ ] Same week across seasons (year over year)
- [ ] Rolling 4-week totals
- [ ] HR / power zone distribution per season
- [ ] RPE or workout feel vs load (scatter)
- [ ] Week types as background bands

## To discuss

- [ ] More metrics beyond TSS/CTL/ATL/TSB? (ideas: runs per week, longest run, pace, zone share, efficiency)
- [ ] Skill "add or edit a metric": build it after doing 1-2 metrics by hand
- [ ] More Garmin data (sleep, HRV, resting HR, stress, Body Battery, weight)
- [ ] MCP server over the training data
- [ ] Share the frontend repo so API changes can be checked against it

## Other

- [ ] Automatic daily sync: a local scheduled task running `scripts.sync_garmin` (there is no sync route anymore)
- [ ] `POST /weeks` to set week types from the frontend (replaces editing `scripts/set_week_data.py`; needs auth first)
- [ ] Importing `jean_cours.db` connects to Atlas, so even `--help` on a script needs the database

## Done

- [x] CLAUDE.md, `.gitignore` for Garmin tokens
- [x] pytest suite
- [x] Week indexes one week late (ISO parsing)
- [x] Weeks sorted as text instead of chronologically
- [x] Garmin login: narrow fallback, never prompt from HTTP
- [x] One Garmin login per sync
- [x] 500 error when no activity matches
- [x] Swagger: response schemas, units, tags (`/docs`)
- [x] `"_id": null` removed from weekly responses
- [x] `/metricsByActivity`: `week` and `metrics` required (422 instead of `[]`)
- [x] History backfill: `activity.py --since YYYY-MM-DD`
- [x] Weeks without runs zero-filled
- [x] `from` / `to` date range on weekly endpoints
- [x] Activity types as a parameter (`types`, default running 1 and 6)
- [x] `get_metric_list_by_activity` no longer mutates the caller's list
- [x] Backfill done for 2025 (321 activities) and 2026 (219)
- [x] `/metricsAvgByWeek` weighted by duration
- [x] hrTSS, CTL, ATL, TSB (`/trainingLoad`, `/trainingLoadByDay`)
- [x] Activity field list: `docs/garmin-activity-fields.md`
- [x] Packages: `jean_cours` (web API) and `garmin_sync` (local), scripts in `scripts/`; `/garmin` route removed
- [x] Python 3.15 venv; dependencies upgraded (FastAPI 0.162, Starlette 1.10, pydantic 2.14, pymongo 4.19, garminconnect 0.3.20, pytest 9.2, httpx2 2.16); garth and the `dotenv` wrapper dropped
- [x] Unique indexes always ensured; type hints fixed
