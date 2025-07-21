import os
from urllib.parse import quote

from api import make_https_request

API_URL = "emojicdn.elk.sh"


def get_emoji(emoji):
    """
    Download the emoji from the API and save it to the cache. (directory: ./emojis)
    If the emoji is already cached, return the path to the emoji.
    """

    # First check if the emoji is already cached.
    if os.path.exists(os.path.join("emojis", f"{emoji}.png")):
        return os.path.abspath(os.path.join("emojis", f"{emoji}.png"))

    url = f"https://{API_URL}/{quote(emoji)}"
    data = make_https_request("GET", url)
    if data is None:
        return os.path.abspath(os.path.join("emojis", "📄.png"))

    # Check if the response contains "Emoji not found" or lacks an <img> tag
    data_str = data.decode("utf-8", errors="ignore")
    if "Emoji not found" in data_str or "<img" not in data_str:
        return os.path.abspath(os.path.join("emojis", "📄.png"))

    # Create emoji image if it doesn't exist.
    with open(os.path.join("emojis", f"{emoji}.png"), "wb") as file:
        file.write(data)

    return os.path.abspath(os.path.join("emojis", f"{emoji}.png"))
