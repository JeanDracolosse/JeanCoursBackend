from jean_cours.db import upsert_week, upsert_week_type


week_type_list = [
    {
        "weekTypeId": 0,
        "label": "Base"
    },
    {
        "weekTypeId": 1,
        "label": "Récupération"
    },
    {
        "weekTypeId": 2,
        "label": "Intensive"
    },
    {
        "weekTypeId": 3,
        "label": "Spécifique"
    }
]

week = {
    "date": "2025-11-10",
    "weekTypeId": 1
}


def set_week_types() -> None:
    for week_type in week_type_list:
        upsert_week_type(week_type)


def set_week() -> None:
    upsert_week(week)


if __name__ == "__main__":
    set_week_types()
    set_week()
