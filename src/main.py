import argparse
from json import dumps
from unicodedata import normalize

from api import search_notion
from items import parse_notion_data
from offline import run_offline_search
from update_data import update_all_pages


def run_online_search(query: str) -> str:
    results = search_notion(query)
    return (
        parse_notion_data(results)
        if results
        else dumps({"items": [{"title": "No results", "arg": ""}]})
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--offline", action="store_true", help="Use local JSON data")
    parser.add_argument(
        "--update", action="store_true", help="Refresh data from Notion API"
    )
    args = parser.parse_args()

    if args.update:
        update_all_pages()
        return

    query = normalize("NFC", " ".join(args.query))

    if args.offline:
        print(run_offline_search(query))
    else:
        print(run_online_search(query))


if __name__ == "__main__":
    main()
