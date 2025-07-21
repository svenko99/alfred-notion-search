import logging
from dataclasses import dataclass, field
from json import dumps
from typing import Optional

from api import download_image
from config import USE_DESKTOP_CLIENT
from get_emojis import get_emoji


@dataclass
class AlfredItem:
    title: str
    arg: str
    icon_path: str
    subtitle: str = field(default="")

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "arg": self.arg,
            "icon": {"path": self.icon_path},
        }


def extract_title(result: dict) -> str:
    try:
        # Case 1: Page in a database
        if result.get("parent", {}).get("type") == "database_id":
            title_info = (
                result.get("properties", {}).get("\ufeffName", {}).get("title", [])
            )
            if title_info:
                return title_info[0].get("plain_text", "Untitled")

        # Case 2: Standalone page
        if result.get("object") == "page":
            title_info = result.get("properties", {}).get("title", {}).get("title", [])
            if title_info:
                return title_info[0].get("plain_text", "Untitled")

        # Fallback: try direct title field
        title_info = result.get("title", [])
        if title_info:
            return title_info[0].get("plain_text", "Untitled")

    except Exception as e:
        logging.error(f"Error extracting title: {e}")

    return "Untitled"


def parse_image(result: dict) -> str:
    try:
        icon = result.get("icon", {})
        icon_type = icon.get("type")

        if icon_type == "emoji":
            return get_emoji(icon["emoji"])
        elif icon_type in ["file", "external"]:
            return download_image(icon[icon_type]["url"])
    except Exception as e:
        logging.error(f"Error parsing image: {e}")

    return "emojis/📄.png"


def build_breadcrumbs(page_id: str, page_map: dict[str, dict]) -> str:
    breadcrumbs = []
    current_page_id = page_id
    while True:
        current_page = page_map.get(current_page_id)
        if not current_page:
            break
        parent_id = current_page.get("parent")
        if not parent_id:
            break
        parent_page = page_map.get(parent_id)
        if not parent_page:
            break
        breadcrumbs.insert(0, parent_page.get("title", ""))
        if parent_page.get("is_top_level", False):
            break
        current_page_id = parent_id
    return " / ".join(breadcrumbs)


def create_item(result: dict, page_map: Optional[dict[str, dict]] = None) -> dict:
    title = extract_title(result)
    icon_path = parse_image(result)
    url = f'notion:{result["url"][6:]}' if USE_DESKTOP_CLIENT else result["url"]
    subtitle = build_breadcrumbs(result["id"], page_map) if page_map else ""

    return AlfredItem(
        title=title, arg=url, icon_path=icon_path, subtitle=subtitle
    ).to_dict()


def parse_notion_data(
    data: list[dict], page_map: Optional[dict[str, dict]] = None
) -> str:
    items = [create_item(result, page_map=page_map) for result in data]
    # Prioritiziraj rezultate z "boljšo" ikono (brez 📄.png)
    if len(items) > 1:
        items.sort(key=lambda item: item["icon"]["path"].endswith("📄.png"))

    return dumps({"items": items}, ensure_ascii=False)
