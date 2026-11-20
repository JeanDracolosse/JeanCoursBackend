# Weekly pipelines group on this numeric key and sort on it, so every
# endpoint returns its per-week arrays in the same chronological order.
WEEK_GROUP_ID = {"year": "$year", "week": "$week"}
SORT_BY_WEEK = {"$sort": {"_id.year": 1, "_id.week": 1}}

INDEX_PIPELINE = [
    {
        "$match": {
            "activityType.typeId": {"$in": [1, 6]}
        }
    },
    {
        "$project": {
            "year": {
                "$isoWeekYear": "$startTimeLocal"
            },
            "week": {
                "$isoWeek": "$startTimeLocal"
            },
        }
    },
    {
        "$group": {
            "_id": WEEK_GROUP_ID
        }
    },
    SORT_BY_WEEK
]

HR_TIME_IN_ZONE_PIPELINE = [
    {
        "$match": {
            "activityType.typeId": {"$in": [1, 6]}
        }
    },
    {
        "$project": {
            "year": {
                "$isoWeekYear": "$startTimeLocal"
            },
            "week": {
                "$isoWeek": "$startTimeLocal"
            },
            "hrTimeInZone_1": 1,
            "hrTimeInZone_2": 1,
            "hrTimeInZone_3": 1,
            "hrTimeInZone_4": 1,
            "hrTimeInZone_5": 1,
        }
    },
    {
        "$group": {
            "_id": WEEK_GROUP_ID,
            "hrTimeInZone_1": {
                "$sum": "$hrTimeInZone_1"
            },
            "hrTimeInZone_2": {
                "$sum": "$hrTimeInZone_2"
            },
            "hrTimeInZone_3": {
                "$sum": "$hrTimeInZone_3"
            },
            "hrTimeInZone_4": {
                "$sum": "$hrTimeInZone_4"
            },
            "hrTimeInZone_5": {
                "$sum": "$hrTimeInZone_5"
            }
        }
    },
    SORT_BY_WEEK,
    {
        "$group": {
            "_id": None,
            "hrTimeInZone_1": {
                "$push": "$hrTimeInZone_1"
            },
            "hrTimeInZone_2": {
                "$push": "$hrTimeInZone_2"
            },
            "hrTimeInZone_3": {
                "$push": "$hrTimeInZone_3"
            },
            "hrTimeInZone_4": {
                "$push": "$hrTimeInZone_4"
            },
            "hrTimeInZone_5": {
                "$push": "$hrTimeInZone_5"
            }
        }
    },
    {
        "$project": {
            "_id": 0,
        }
    },
]

POWER_TIME_IN_ZONE_PIPELINE = [
    {
        "$match": {
            "activityType.typeId": {"$in": [1, 6]}
        }
    },
    {
        "$project": {
            "year": {
                "$isoWeekYear": "$startTimeLocal"
            },
            "week": {
                "$isoWeek": "$startTimeLocal"
            },
            "powerTimeInZone_1": 1,
            "powerTimeInZone_2": 1,
            "powerTimeInZone_3": 1,
            "powerTimeInZone_4": 1,
            "powerTimeInZone_5": 1,
        }
    },
    {
        "$group": {
            "_id": WEEK_GROUP_ID,
            "powerTimeInZone_1": {
                "$sum": "$powerTimeInZone_1"
            },
            "powerTimeInZone_2": {
                "$sum": "$powerTimeInZone_2"
            },
            "powerTimeInZone_3": {
                "$sum": "$powerTimeInZone_3"
            },
            "powerTimeInZone_4": {
                "$sum": "$powerTimeInZone_4"
            },
            "powerTimeInZone_5": {
                "$sum": "$powerTimeInZone_5"
            }
        }
    },
    SORT_BY_WEEK,
    {
        "$group": {
            "_id": None,
            "powerTimeInZone_1": {
                "$push": "$powerTimeInZone_1"
            },
            "powerTimeInZone_2": {
                "$push": "$powerTimeInZone_2"
            },
            "powerTimeInZone_3": {
                "$push": "$powerTimeInZone_3"
            },
            "powerTimeInZone_4": {
                "$push": "$powerTimeInZone_4"
            },
            "powerTimeInZone_5": {
                "$push": "$powerTimeInZone_5"
            }
        }
    },
    {
        "$project": {
            "_id": 0,
        }
    },
]

DISTANCE_PIPELINE = [
    {
        "$match": {
            "activityType.typeId": {"$in": [1, 6]}
        }
    },
    {
        "$project": {
            "year": {
                "$isoWeekYear": "$startTimeLocal"
            },
            "week": {
                "$isoWeek": "$startTimeLocal"
            },
            "distance": 1,
            "elevationGain": 1,
            "elevationLoss": 1,
            "fullKilometerEffort": {
                "$add": [
                    "$distance",
                    {
                        "$multiply": ["$elevationGain", 10]
                    },
                    {
                        "$multiply": ["$elevationLoss", 3]
                    }
                ]
            },
            "kilometerEffort": {
                "$add": [
                    "$distance",
                    {
                        "$multiply": ["$elevationGain", 10]
                    }
                ]
            }
        }
    },
    {
        "$group": {
            "_id": WEEK_GROUP_ID,
            "distance": {
                "$sum": "$distance"
            },
            "elevationGain": {
                "$sum": "$elevationGain"
            },
            "elevationLoss": {
                "$sum": "$elevationLoss"
            },
            "kilometerEffort": {
                "$sum": "$kilometerEffort"
            },
            "fullKilometerEffort": {
                "$sum": "$fullKilometerEffort"
            }
        }
    },
    SORT_BY_WEEK,
    {
        "$group": {
            "_id": None,
            "distance": {
                "$push": "$distance"
            },
            "elevationGain": {
                "$push": "$elevationGain"
            },
            "elevationLoss": {
                "$push": "$elevationLoss"
            },
            "kilometerEffort": {
                "$push": "$kilometerEffort"
            },
            "fullKilometerEffort": {
                "$push": "$fullKilometerEffort"
            }
        }
    }
]


def get_metric_list_pipeline_by_week(metric_list: list, aggregation: str) -> list[dict]:
    return [
        {
            "$match": {
                "activityType.typeId": {"$in": [1, 6]}
            }
        },
        {
            "$project": {
                "year": {
                    "$isoWeekYear": "$startTimeLocal"
                },
                "week": {
                    "$isoWeek": "$startTimeLocal"
                },

                **{metric: 1 for metric in metric_list}
            }
        },
        {
            "$group": {
                "_id": WEEK_GROUP_ID,
                **{metric: {
                    f"${aggregation}": f"${metric}"
                } for metric in metric_list}
            }
        },
        SORT_BY_WEEK,
        {
            "$group": {
                "_id": None,
                **{metric: {
                    "$push": f"${metric}"
                } for metric in metric_list}
            }
        }
    ]


def get_metric_list_pipeline_by_activity(year: int, week: int, metric_list: list) -> list[dict]:
    return [
        {"$match": {
            "activityType.typeId": {"$in": [1, 6]}
        }
        },
        {"$project": {
            "year": {"$isoWeekYear": "$startTimeLocal"
                     },
            "week": {"$isoWeek": "$startTimeLocal"
                     },
            **{metric: 1 for metric in metric_list}
        }
        },
        {"$match": {
            "year": year,
            "week": week,
        }
        },
        {"$sort": {
            "startTimeLocal": 1
        }
        },
        {"$group": {
            "_id": None,
            **{metric: {
                "$push": f"${metric}"
            } for metric in metric_list}
        }
        }
    ]


def get_week_types_pipeline() -> list[dict]:
    return [
        {"$lookup":
         {
             "from": "weekTypes",
             "localField": "weekTypeId",
             "foreignField": "weekTypeId",
             "as": "label"
         }
         },
        {"$unwind":
         {
             "path": "$label"
         }
         },
        {"$project":
         {
             "_id": 0,
             "date": 1,
             "label": "$label.label"
         }
         }
    ]
