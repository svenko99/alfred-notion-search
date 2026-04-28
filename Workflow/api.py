import json
import logging
import os
from typing import Optional, Union
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from config import API, ENABLE_IMAGES

DEFAULT_ICON = "emojis/📄.png"
REQUEST_TIMEOUT = 15


def make_https_request(
    method: str,
    url: str,
    body: Union[bytes, str, None] = None,
    headers: Optional[dict] = None,
) -> Optional[bytes]:
    if isinstance(body, str):
        body = body.encode("utf-8")
    req = Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return resp.read()
    except HTTPError as e:
        logging.error(f"HTTP {e.code} on {method} {url}: {e.reason}")
    except URLError as e:
        logging.error(f"Network error on {method} {url}: {e.reason}")
    except OSError as e:
        logging.error(f"OSError on {method} {url}: {e}")
    return None


def get_notion_headers() -> dict:
    return {
        "Authorization": f"Bearer {API}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }


def search_notion(query: str, page_size: int = 9) -> list[dict]:
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
        "POST",
        "https://api.notion.com/v1/search",
        body=payload,
        headers=get_notion_headers(),
    )
    return json.loads(data).get("results", []) if data else []


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


def download_image(url: str, allow_network: bool = True) -> str:
    if not ENABLE_IMAGES:
        return DEFAULT_ICON

    parsed_url = urlparse(url)
    filename = f"custom_images/{parsed_url.path.replace('/', '-')}"

    if os.path.exists(filename):
        return filename
    if not allow_network:
        return DEFAULT_ICON

    data = make_https_request("GET", url)
    if data:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            f.write(data)
        return filename

    return DEFAULT_ICON
