from dotenv import load_dotenv
import os

load_dotenv(".env")

TOKEN = os.getenv("TELEGRAM_TOKEN")
PROXY = "socks5://127.0.0.1:9050"

USERS = {
    447411595: "Коля",
    697676993: "Игнат",
    419576201: "Саша",
    406974543: "Никита",
    441085220: "Чонг",
}

ADMIN = 447411595


class Emoji:
    FALSE = "❌"
    TRUE = "✅"
