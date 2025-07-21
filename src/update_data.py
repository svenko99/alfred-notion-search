import json
import logging
import time

from api import fetch_all_pages
from items import parse_image, extract_title


def save_page_titles(results: list[dict]) -> None:
    page_map = {}
    for page in results:
        page_id = page.get("id")
        title = extract_title(page)
        parent = page.get("parent", {})
        parent_type = parent.get("type")
        if parent_type == "workspace":
            is_top_level = True
            parent_id = ""
        elif parent_type == "database_id":
            is_top_level = False
            parent_id = parent.get("database_id", "") or ""
        else:
            is_top_level = False
            parent_id = parent.get("page_id", "") or ""
        if page_id and title:
            page_map[page_id] = {
                "title": title,
                "is_top_level": is_top_level,
                "parent": parent_id,
            }
    with open("page_titles.json", "w", encoding="utf-8") as f:
        json.dump(page_map, f, indent=2, ensure_ascii=False)


def update_all_pages(output_file: str = "all_pages_data.json") -> None:
    logging.basicConfig(level=logging.INFO)
    start = time.time()

    # Fetch all pages from the API
    results = fetch_all_pages()

    # Extract and save page titles keyed by page IDs
    save_page_titles(results)

    # Attempt to parse and download images for each page, logging failures
    for result in results:
        try:
            _ = parse_image(result)
        except Exception as e:
            logging.warning(f"Failed to download image: {e}")

    # Save the full results data to the output JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            {"object": "list", "results": results, "type": "page_or_database"},
            f,
            indent=2,
            ensure_ascii=False,
        )

    # Print the time taken to update the data
    elapsed_time = round(time.time() - start)
    print(f"Notion data has been updated. It took {elapsed_time} seconds.")
