import os
from urllib.parse import quote

from api import make_https_request

EMOJI_DIR = "emojis"
FALLBACK = os.path.abspath(os.path.join(EMOJI_DIR, "📄.png"))
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
API_URL = "emojicdn.elk.sh"


def get_emoji(emoji: str) -> str:
    path = os.path.join(EMOJI_DIR, f"{emoji}.png")
    if os.path.exists(path):
        return os.path.abspath(path)

    data = make_https_request("GET", f"https://{API_URL}/{quote(emoji)}")
    if not data or not data.startswith(PNG_MAGIC):
        return FALLBACK

    os.makedirs(EMOJI_DIR, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return os.path.abspath(path)
