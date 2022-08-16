import os

from dotenv import load_dotenv
from loguru import logger as log

load_dotenv()

DEFAULT_TOKEN = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"

TOKEN = os.environ.get("TELEGRAM_TOKEN", DEFAULT_TOKEN)
LOG_PATH = os.environ.get("LOG_PATH", "./")
DB_PATH = os.environ.get("DB_PATH", "./")

if TOKEN == DEFAULT_TOKEN:
    log.warning(f"Using default token. Bot wont work!")

PROXY = "socks5://127.0.0.1:9050"
