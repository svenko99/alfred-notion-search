import json
import logging
import os
from typing import Optional
from urllib.parse import urlparse

import requests
from config import API, ENABLE_IMAGES


def make_https_request(
    method: str, url: str, body=None, headers=None
) -> Optional[bytes]:
    try:
        response = requests.request(method, url, data=body, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTPS request failed: {e}")
        return None


def get_notion_headers() -> dict:
    return {
        "Authorization": f"Bearer {API}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }


def search_notion(query: str, page_size: int = 9) -> list[dict]:
    headers = get_notion_headers()
    payload = json.dumps(
        {
            "query": query,
            "page_size": page_size,
            "sort": {
                "direction": "descending",
                "timestamp": "last_edited_time",
            },
        }
    )
    data = make_https_request(
        "POST", "https://api.notion.com/v1/search", body=payload, headers=headers
    )

    return json.loads(data.decode()).get("results", []) if data else []


def fetch_all_pages() -> list[dict]:
    headers = get_notion_headers()
    payload = {
        "sort": {"direction": "descending", "timestamp": "last_edited_time"},
    }

    results = []
    while True:
        response_data = make_https_request(
            "POST",
            "https://api.notion.com/v1/search",
            body=json.dumps(payload),
            headers=headers,
        )
        if not response_data:
            break

        data = json.loads(response_data)
        results.extend(data["results"])

        if not data.get("has_more", False):
            break
        payload["start_cursor"] = data.get("next_cursor")

    return results


def download_image(url: str) -> str:
    if not ENABLE_IMAGES:
        return "emojis/📄.png"

    parsed_url = urlparse(url)
    filename = f"custom_images/{parsed_url.path.replace('/', '-')}"

    if os.path.exists(filename):
        return filename

    data = make_https_request("GET", url)
    if data:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            f.write(data)
        return filename

    return "emojis/📄.png"
