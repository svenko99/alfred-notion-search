import os

API = os.environ.get("NOTION_API")
USE_DESKTOP_CLIENT = os.environ.get("USE_DESKTOP_CLIENT") == "1"
ENABLE_IMAGES = os.environ.get("ENABLE_IMAGES") == "1"
