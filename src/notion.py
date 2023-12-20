import os
import sys
import requests
from json import dumps, loads
from urllib.parse import urlparse
from unicodedata import normalize
import logging

from get_emojis import get_emoji

API = os.environ["NOTION_API"]
USE_DESKTOP_CLIENT = os.environ["USE_DESKTOP_CLIENT"] == "1"
ENABLE_IMAGES = os.environ["ENABLE_IMAGES"] == "1"


def make_https_request(method, url, body=None, headers=None):
    try:
        response = requests.request(method, url, data=body, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTPS request failed: {e}")
        return None


def get_notion_data(search: str) -> dict:
    headers = {
        "Authorization": f"Bearer {API}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    json_data = dumps(
        {
            "query": search,
            "page_size": 9,
            "sort": {
                "direction": "descending",
                "timestamp": "last_edited_time",
            },
        }
    )

    data = make_https_request(
        "POST", "https://api.notion.com/v1/search", body=json_data, headers=headers
    )
    if data:
        return loads(data.decode())["results"]
    return []


def download_image(url: str) -> str:
    if not ENABLE_IMAGES:
        return "emojis/📄.png"

    parsed_url = urlparse(url)
    filename = f'custom_images/{parsed_url.path.replace("/", "-")}'

    if os.path.exists(filename):
        return filename

    data = make_https_request("GET", url)

    if data:
        with open(filename, "wb") as f:
            f.write(data)
        return filename

    return "emojis/📄.png"


def extract_title(result: dict) -> str:
    if result["parent"]["type"] == "database_id":
        get_name = result["properties"]["Name"]["title"]
        if get_name:
            return get_name[0]["plain_text"]
        else:
            return "Untitled"
    else:
        if result["object"] == "page":
            partial_title = result.get("properties", {}).get("title", {}).get("title")
            if partial_title:
                return partial_title[0]["plain_text"]
            else:
                return "Untitled"

        else:
            return result["title"][0]["plain_text"]


def parse_image(result: dict) -> str:
    try:
        icon_type = result.get("icon", {}).get("type")
        if icon_type == "emoji":
            return get_emoji(result["icon"]["emoji"])
        elif icon_type in ["file", "external"]:
            return download_image(result["icon"][icon_type]["url"])
    except Exception as e:
        logging.error(f"Error parsing image: {e}")

    return "emojis/📄.png"


def create_item(result: dict) -> dict:
    image = parse_image(result)
    url = f'notion:{result["url"][6:]}' if USE_DESKTOP_CLIENT else result["url"]
    title = extract_title(result)

    return {"title": title, "arg": url, "icon": {"path": image}}


def parse_notion_data(data: dict) -> str:
    items = [create_item(result) for result in data]
    return dumps({"items": items})


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    search = normalize("NFC", " ".join(sys.argv[1:]))
    data = get_notion_data(search)

    if data:
        print(parse_notion_data(data))
    else:
        print(dumps({"items": [{"title": "No pages found", "arg": ""}]}))
