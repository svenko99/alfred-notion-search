import json
import os

from items import create_item, parse_notion_data
from thefuzz import process

FUZZY_SEARCH_SCORE = 90


def load_local_data(file_path: str = "all_pages_data.json") -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data.get("results", [])


def load_page_map(file_path: str = "page_titles.json") -> dict[str, dict]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def fuzzy_search_titles(query: str, all_titles: set[str]) -> set[str]:
    matches = process.extract(
        query, all_titles, limit=10, scorer=process.fuzz.partial_ratio
    )
    return {match[0] for match in matches if match[1] >= FUZZY_SEARCH_SCORE}


def run_offline_search(query: str) -> str:
    if not os.path.exists("all_pages_data.json"):
        return json.dumps(
            {
                "items": [
                    {
                        "title": "Local data not found",
                        "subtitle": "Run 'nupdate' to fetch pages",
                        "arg": "",
                    }
                ]
            },
            ensure_ascii=False,
        )

    results = load_local_data()
    page_map = load_page_map()
    items = [create_item(result, page_map=page_map) for result in results]
    all_titles = sorted(item["title"] for item in items)
    matched_titles = fuzzy_search_titles(query, all_titles)

    if not query.strip():
        return parse_notion_data(results[:6], page_map=page_map)

    if matched_titles:
        matched_items = [item for item in items if item["title"] in matched_titles]
        matched_items.sort(
            key=lambda item: item["icon"]["path"].endswith("📄.png")
        )  # Sort so that items without 📄.png come last in Alfred
        return json.dumps({"items": matched_items}, ensure_ascii=False)

    return json.dumps(
        {"items": [{"title": "No results found", "arg": ""}]}, ensure_ascii=False
    )
