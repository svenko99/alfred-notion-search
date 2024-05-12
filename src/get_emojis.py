import os
import http.client
from urllib.parse import quote


API_URL = "emojicdn.elk.sh"


def get_emoji(emoji):
    """
    Download the emoji from the API and save it to the cache. (directory: ./emojis)
    If the emoji is already cached, return the path to the emoji.
    """

    # First check if the emoji is already cached.
    if os.path.exists(os.path.join("emojis", f"{emoji}.png")):
        return os.path.abspath(os.path.join("emojis", f"{emoji}.png"))

    connection = http.client.HTTPSConnection(API_URL)
    path = f"/{quote(emoji)}"

    connection.request("GET", path)
    response = connection.getresponse()

    # Create emoji image if it doesn't exist.
    with open(os.path.join("emojis", f"{emoji}.png"), "wb") as file:
        file.write(response.read())

    return os.path.abspath(os.path.join("emojis", f"{emoji}.png"))
