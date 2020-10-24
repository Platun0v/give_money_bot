from dotenv import load_dotenv
import os

load_dotenv(".env")

TOKEN = os.getenv("TELEGRAM_TOKEN")
PROXY = "socks5://127.0.0.1:9050"

USERS = {
    447411595: "Коля",
}
