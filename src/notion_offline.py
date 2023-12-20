import sys
from json import dumps, load
from unicodedata import normalize

from thefuzz import process
import notion


def get_notion_data() -> dict:
    with open("all_pages_data.json", "r") as file:
        data = load(file)
    return data["results"]


def get_fuzzy_search_results(search: str, data: list) -> list:
    """Perform a fuzzy search on the provided data."""
    return [
        result
        for result in process.extract(
            search, data, limit=10, scorer=process.fuzz.partial_ratio
        )
        if result[1] >= 77
    ]


def create_alfred_json(results: list, fuzzy_titles: set) -> str:
    """Create a JSON string formatted for Alfred from the search results."""
    items = [result for result in results if result["title"] in fuzzy_titles]
    return dumps({"items": items})


def display_recently_viewed_pages():
    data = get_notion_data()[:6]
    notion_page_info = notion.parse_notion_data(data)
    print(notion_page_info)


def main():
    search = normalize("NFC", " ".join(sys.argv[1:]))
    data = [notion.create_item(result) for result in get_notion_data()]

    titles = {item["title"] for item in data}
    extracted_titles = {
        result[0] for result in get_fuzzy_search_results(search, titles)
    }

    if extracted_titles:
        print(create_alfred_json(data, extracted_titles))
    elif not search.strip():
        display_recently_viewed_pages()
    else:
        print(dumps({"items": [{"title": "No pages found", "arg": ""}]}))


if __name__ == "__main__":
    main()
