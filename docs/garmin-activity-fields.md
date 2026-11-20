# Garmin activity fields

Fields of an activity document in the `activities` collection, read from a 2026 run (2026-11-20). Names and types only.

Any numeric field works with the `metrics` query parameter of `/metricsSumByWeek`, `/metricsAvgByWeek` and `/metricsByActivity`.

Units follow Garmin's activity JSON: seconds, meters, meters per second, bpm, watts.

## Volume

| Field | Type | Unit |
|---|---|---|
| `distance` | float | m |
| `duration` | float | s (timer time; weights `/metricsAvgByWeek`) |
| `movingDuration` | float | s |
| `elapsedDuration` | float | s |
| `calories`, `bmrCalories` | float | kcal |
| `steps` | int | |
| `lapCount` | int | |
| `waterEstimated` | float | ml |
| `moderateIntensityMinutes`, `vigorousIntensityMinutes` | int | min |

## Intensity

| Field | Type | Unit |
|---|---|---|
| `averageHR`, `maxHR` | float | bpm |
| `hrTimeInZone_1` … `hrTimeInZone_5` | float | s |
| `averageSpeed`, `maxSpeed` | float | m/s |
| `avgGradeAdjustedSpeed` | float | m/s |
| `avgPower`, `maxPower`, `normPower` | float | W |
| `powerTimeInZone_1` … `powerTimeInZone_5` | float | s |
| `fastestSplit_1000`, `fastestSplit_1609`, `fastestSplit_5000` | float | s |
| `maxVerticalSpeed` | float | m/s |

## Running form

| Field | Type | Unit |
|---|---|---|
| `averageRunningCadenceInStepsPerMinute`, `maxRunningCadenceInStepsPerMinute` | float | steps/min |
| `maxDoubleCadence` | float | steps/min |
| `avgStrideLength` | float | cm |
| `avgVerticalOscillation` | float | cm |
| `avgGroundContactTime` | float | ms |
| `avgVerticalRatio` | float | % |

## Garmin scores

| Field | Type |
|---|---|
| `activityTrainingLoad` | float |
| `aerobicTrainingEffect`, `anaerobicTrainingEffect` | float |
| `aerobicTrainingEffectMessage`, `anaerobicTrainingEffectMessage`, `trainingEffectLabel` | str |
| `vO2MaxValue` | float |
| `differenceBodyBattery` | int |

## From the FIT file (added by the sync)

| Field | Type |
|---|---|
| `workoutFeel` | int |
| `workoutRpe` | int |

## Terrain and weather

| Field | Type | Unit |
|---|---|---|
| `elevationGain`, `elevationLoss` | float | m |
| `minElevation`, `maxElevation`, `avgElevation` | float | m |
| `minTemperature`, `maxTemperature` | float | °C |
| `startLatitude`, `startLongitude`, `endLatitude`, `endLongitude` | float | degrees |
| `locationName` | str | |

## Identity and time

`activityId` (Int64), `activityUUID`, `activityName`, `activityType.typeId` / `.typeKey` / `.parentTypeId`, `sportTypeId`, `eventType.typeId` / `.typeKey`, `startTimeLocal`, `startTimeGMT`, `endTimeGMT` (datetime), `beginTimestamp` (Int64), `timeZoneId`, `deviceId`, `manufacturer`.

## Flags and metadata (not metrics)

`hasPolyline`, `hasSplits`, `hasHeatMap`, `hasImages`, `hasVideo`, `hasIntensityIntervals`, `isPR` / `pr`, `isFavorite` / `favorite`, `isManualActivity` / `manualActivity`, `isParent` / `parent`, `isPurposeful` / `purposeful`, `isAtpActivity` / `atpActivity`, `isAutoCalcCalories` / `autoCalcCalories`, `isElevationCorrected` / `elevationCorrected`, `isDecoDive` / `decoDive`, `qualifyingDive`, `userPro`, `userRoles`, `privacy.*`, `owner*`, `splitSummaries`, `summarizedDiveInfo.*`.
