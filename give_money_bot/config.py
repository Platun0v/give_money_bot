import os

from dotenv import load_dotenv

load_dotenv()


DEFAULT_TOKEN = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"

TOKEN = os.environ.get("TELEGRAM_TOKEN", DEFAULT_TOKEN)
LOG_PATH = os.environ.get("LOG_PATH", "./")
DB_PATH = os.environ.get("DB_PATH", "./")

# if TOKEN == DEFAULT_TOKEN:
#     logger.warning(f"Using default token. Bot want work!")

PROXY = "socks5://127.0.0.1:9050"
