import os
import time
from json import dumps, loads
from notion import make_https_request, API, download_image


start_time = time.time()


def get_all_pages(api_key):
    """Fetches all pages from Notion API and writes them to a file."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    json_data = {"sort": {"direction": "descending", "timestamp": "last_edited_time"}}
    all_pages_data = {"object": "list", "results": [], "type": "page_or_database"}

    while True:
        response_data = make_https_request(
            "POST",
            "https://api.notion.com/v1/search",
            body=dumps(json_data),
            headers=headers,
        )
        try:
            data = loads(response_data)
        except Exception as e:
            print(f"Error parsing response data: {e}")
            break

        all_pages_data["results"].extend(data["results"])

        if not data.get("has_more", False):
            break
        json_data["start_cursor"] = data.get("next_cursor")

    # download all images
    for result in all_pages_data["results"]:
        try:
            icon_type = result.get("icon", {}).get("type")
            if icon_type in ["file", "external"]:
                download_image(result["icon"][icon_type]["url"])
        except Exception:
            pass

    with open("all_pages_data.json", "w") as file:
        file.write(dumps(all_pages_data, indent=2, ensure_ascii=False))


def main():
    get_all_pages(API)
    subtitle = f"It took {round(time.time() - start_time)} seconds."
    alfred_json = f"Notion data has been updated.\n{subtitle}"
    print(alfred_json)


if __name__ == "__main__":
    main()
