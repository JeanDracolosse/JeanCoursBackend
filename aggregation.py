INDEX_PIPELINE = [
    {
        "$match": {
            "activityType.typeId": 1
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
            "_id": {
                "$concat": [
                  {
                      "$toString": "$year"
                  },
                    "-",
                    {"$toString": "$week"
                     }
                ]
            }
        }
    },
    {
        "$sort": {
            "_id": 1
        }
    }
]

HR_TIME_IN_ZONE_PIPELINE = [
    {
        "$match": {
            "activityType.typeId": 1
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
            "_id": {
                "$concat": [
                    {
                        "$toString": "$year"
                    },
                    "_",
                    {
                        "$toString": "$week"
                    }
                ]
            },
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
    {
        "$sort":
            {
                "_id": 1
            }
    },
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

DISTANCE_PIPELINE = [
    {
        "$match": {
            "activityType.typeId": 1
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
            "elevationGain": 1
        }
    },
    {
        "$group": {
            "_id": {
                "$concat": [
                    {
                        "$toString": "$year"
                    },
                    "_",
                    {
                        "$toString": "$week"
                    }
                ]
            },
            "distance": {
                "$sum": "$distance"
            },
            "elevationGain": {
                "$sum": "$elevationGain"
            }
        }
    },
    {
        "$sort":
            {
                "_id": 1
            }
    },
    {
        "$group": {
            "_id": None,
            "distance": {
                "$push": "$distance"
            },
            "elevationGain": {
                "$push": "$elevationGain"
            }
        }
    },
    {
        "$project": {
            "_id": 0,
        }
    },
]