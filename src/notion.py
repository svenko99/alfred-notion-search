import os
import sys
from json import dumps

import requests


API = os.environ["NOTION_API"]
USE_DESKTOP_CLIENT = os.environ["USE_DESKTOP_CLIENT"] == "1"


def get_notion_data(search: str) -> dict:
    HEADERS = {
        "Authorization": f"Bearer {API}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    JSON_DATA = {
        "query": search,
        "page_size": 10,
        "sort": {
            "direction": "descending",
            "timestamp": "last_edited_time",
        },
    }

    with requests.Session() as session:
        session.headers.update(HEADERS)
        response = session.post("https://api.notion.com/v1/search", json=JSON_DATA)
        data = response.json()
        return data["results"]


def parse_emoji(result: dict) -> str:
    try:
        return result["icon"]["emoji"]
    except Exception:
        return "📄"  # If the page doesn't have an emoji or is using a custom icon.


def create_item(result: dict) -> dict:
    emoji = parse_emoji(result)
    url = (
        f'notion:{result["url"][6:]}' if USE_DESKTOP_CLIENT else result["url"]
    )  # Change https:// to notion:// if using the desktop client.

    if result["parent"]["type"] == "database_id":  # Handle database pages
        title = result["properties"]["Name"]["title"][0]["plain_text"]
    else:
        title = (
            result["properties"]["title"]["title"][0]["plain_text"]  # This is for pages
            if result["object"] == "page"
            else result["title"][0]["plain_text"]  # This is for databases
        )

    return {"title": f"{emoji} {title}", "arg": url}


def parse_notion_data(data: dict) -> dict:
    items = [
        create_item(result)
        for result in data
        if result["object"] in ["page", "database"]
    ]
    return dumps({"items": items})


if __name__ == "__main__":
    if data := get_notion_data("".join(sys.argv[1:])):
        print(parse_notion_data(data))
    else:
        print(dumps({"items": [{"title": "No results found", "arg": ""}]}))
