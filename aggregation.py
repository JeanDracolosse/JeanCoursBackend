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

POWER_TIME_IN_ZONE_PIPELINE = [
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
            "powerTimeInZone_1": 1,
            "powerTimeInZone_2": 1,
            "powerTimeInZone_3": 1,
            "powerTimeInZone_4": 1,
            "powerTimeInZone_5": 1,
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
    {
        "$sort":
            {
                "_id": 1
            }
    },
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
    {
        "$sort": {
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
