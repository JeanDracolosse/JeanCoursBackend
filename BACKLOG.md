# Backlog

One topic at a time. Move an item to Done when it's committed.

## Next

- [ ] Pick the next topic

## Later

- [ ] `groupBy=month|season` (week only for now)
- [ ] Define "season" (calendar year, race to race, or custom dates in Mongo?)

## Graph ideas

- [ ] Same week across seasons (year over year)
- [ ] Rolling 4-week totals
- [ ] HR / power zone distribution per season
- [ ] RPE or workout feel vs load (scatter)
- [ ] Week types as background bands

## To discuss

- [ ] New metrics: which ones?
- [ ] Skill "add or edit a metric": build it after doing 1-2 metrics by hand
- [ ] More Garmin data (sleep, HRV, resting HR, stress, Body Battery, weight)
- [ ] MCP server over the training data
- [ ] Share the frontend repo so API changes can be checked against it

## Other

- [ ] Automatic daily sync instead of calling `/garmin` by hand
- [ ] `POST /weeks` to set week types from the frontend (replaces editing `setWeekData.py`)
- [ ] Security: API is open on `0.0.0.0` with no auth (fine at home, not if deployed)
- [ ] Unique indexes only created on empty collections (`mongo.py` `__get_or_create_collection`)
- [ ] Importing `mongo` connects to Atlas, so even `activity.py --help` needs the database
- [ ] Wrong type hints (`-> None` on some functions that return data)

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
