import os

from dotenv import load_dotenv

load_dotenv(".env")

TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
LOG_PATH = os.environ.get("LOG_PATH", "./")
DB_PATH = os.environ.get("DB_PATH", "./")

PROXY = "socks5://127.0.0.1:9050"
