import json
import os
import time

from items import create_item

DATA_PATH = "all_pages_data.json"
TITLES_PATH = "page_titles.json"
STALE_AFTER_DAYS = 1
DEFAULT_ICON = "emojis/📄.png"


def load_local_data() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file).get("results", [])


def load_page_map() -> dict[str, dict]:
    try:
        with open(TITLES_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def _stale_days() -> float:
    try:
        return (time.time() - os.path.getmtime(DATA_PATH)) / 86400
    except OSError:
        return 0.0


def run_offline_search(_query: str) -> str:
    if not os.path.exists(DATA_PATH):
        return json.dumps(
            {
                "items": [
                    {
                        "title": "Local data not found",
                        "subtitle": "Run 'nupdate' to fetch pages",
                        "arg": "",
                        "valid": False,
                    }
                ]
            },
            ensure_ascii=False,
        )

    page_map = load_page_map()
    items = [
        create_item(r, page_map=page_map, allow_network=False)
        for r in load_local_data()
    ]
    if len(items) > 1:
        items.sort(key=lambda i: i["icon"]["path"].endswith("📄.png"))

    days = int(_stale_days())
    if days >= STALE_AFTER_DAYS:
        items.insert(
            0,
            {
                "title": f"⚠ Local data is {days} day{'s' if days != 1 else ''} old",
                "subtitle": "Type 'nupdate' to refresh",
                "arg": "",
                "valid": False,
                "icon": {"path": DEFAULT_ICON},
            },
        )

    return json.dumps({"items": items}, ensure_ascii=False)
