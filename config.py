from dotenv import load_dotenv
import os

load_dotenv(".env")

TOKEN = os.getenv("TELEGRAM_TOKEN")

USERS = {
    447411595: "Коля",
}
