import fcntl
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

from api import fetch_all_pages
from items import extract_title, parse_image

IMAGE_DOWNLOAD_WORKERS = 16
DATA_PATH = "all_pages_data.json"
TITLES_PATH = "page_titles.json"
LOCK_PATH = ".sync.lock"


@contextmanager
def sync_lock():
    f = open(LOCK_PATH, "w")
    try:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            yield False
            return
        yield True
    finally:
        f.close()


def _write_json_atomic(path: str, data) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def save_page_titles(results: list[dict]) -> None:
    page_map = {}
    for page in results:
        page_id = page.get("id")
        title = extract_title(page)
        parent = page.get("parent", {})
        parent_type = parent.get("type")
        if parent_type == "workspace":
            is_top_level, parent_id = True, ""
        elif parent_type == "database_id":
            is_top_level, parent_id = False, parent.get("database_id", "") or ""
        else:
            is_top_level, parent_id = False, parent.get("page_id", "") or ""
        if page_id and title:
            page_map[page_id] = {
                "title": title,
                "is_top_level": is_top_level,
                "parent": parent_id,
            }
    _write_json_atomic(TITLES_PATH, page_map)


def _safe_parse_image(result: dict) -> None:
    try:
        parse_image(result)
    except Exception as e:
        logging.warning(f"Failed to download image: {e}")


def update_all_pages() -> None:
    with sync_lock() as got:
        if not got:
            print("Sync already in progress")
            return

        try:
            start = time.time()
            results = fetch_all_pages()
            if not results:
                logging.error("No pages fetched (check NOTION_API)")
                print("Sync failed: no pages fetched (check NOTION_API)")
                return

            save_page_titles(results)

            with ThreadPoolExecutor(max_workers=IMAGE_DOWNLOAD_WORKERS) as pool:
                list(pool.map(_safe_parse_image, results))

            _write_json_atomic(
                DATA_PATH,
                {"object": "list", "results": results, "type": "page_or_database"},
            )

            elapsed = round(time.time() - start)
            print(f"Notion data updated ({elapsed}s, {len(results)} pages)")
        except Exception as e:
            logging.exception("Sync failed")
            print(f"Sync failed: {e}")
