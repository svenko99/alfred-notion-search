import logging
from dataclasses import dataclass, field
from json import dumps
from typing import Optional

from api import download_image
from config import USE_DESKTOP_CLIENT
from get_emojis import get_emoji


@dataclass
class AlfredItem:
    uid: str
    title: str
    arg: str
    icon_path: str
    subtitle: str = field(default="")
    match: str = field(default="")

    def to_dict(self) -> dict:
        item = {
            "uid": self.uid,
            "title": self.title,
            "subtitle": self.subtitle,
            "arg": self.arg,
            "icon": {"path": self.icon_path},
        }
        if self.match:
            item["match"] = self.match
        return item


def extract_title(result: dict) -> str:
    try:
        if result.get("object") == "database":
            title_fragments = result.get("title", [])
            if title_fragments:
                return "".join(frag.get("plain_text", "") for frag in title_fragments)

        for prop in result.get("properties", {}).values():
            if prop.get("type") == "title":
                title_fragments = prop.get("title", [])
                if title_fragments:
                    return "".join(frag.get("plain_text", "") for frag in title_fragments)
    except Exception as e:
        logging.error(f"Error extracting title: {e}")

    return "Untitled"


def parse_image(result: dict, allow_network: bool = True) -> str:
    try:
        icon = result.get("icon")
        if not icon:
            return "emojis/📄.png"

        icon_type = icon.get("type")
        if icon_type == "emoji":
            return get_emoji(icon["emoji"])
        if icon_type in ("file", "external"):
            return download_image(icon[icon_type]["url"], allow_network=allow_network)
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


def create_item(
    result: dict,
    page_map: Optional[dict[str, dict]] = None,
    allow_network: bool = True,
) -> dict:
    title = extract_title(result)
    icon_path = parse_image(result, allow_network=allow_network)
    url = f'notion:{result["url"][6:]}' if USE_DESKTOP_CLIENT else result["url"]
    subtitle = build_breadcrumbs(result["id"], page_map) if page_map else ""
    match = f"{title} {subtitle}".strip() if subtitle else ""

    return AlfredItem(
        uid=result["id"],
        title=title,
        arg=url,
        icon_path=icon_path,
        subtitle=subtitle,
        match=match,
    ).to_dict()


def parse_notion_data(
    data: list[dict],
    page_map: Optional[dict[str, dict]] = None,
    allow_network: bool = True,
) -> str:
    items = [
        create_item(result, page_map=page_map, allow_network=allow_network)
        for result in data
    ]
    if len(items) > 1:
        items.sort(key=lambda item: item["icon"]["path"].endswith("📄.png"))
    return dumps({"items": items}, ensure_ascii=False)
