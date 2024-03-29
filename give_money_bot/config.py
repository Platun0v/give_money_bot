from loguru import logger as log
from pydantic import BaseSettings

DEFAULT_TOKEN = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"

# TOKEN = os.environ.get("TELEGRAM_TOKEN", DEFAULT_TOKEN)
# LOG_PATH = os.environ.get("LOG_PATH", "./")
# DB_PATH = os.environ.get("DB_PATH", "./")
# ADMIN_ID = os.environ.get("ADMIN_ID", "447411595")
#
# if TOKEN == DEFAULT_TOKEN:
#     log.warning("Using default token. Bot wont work!")
#
# PROXY = "socks5://127.0.0.1:9050"
#
# PROMETHEUS_PORT = int(os.environ.get("PROMETHEUS_PORT", 9121))


class Settings(BaseSettings, env_file=".env"):
    telegram_token: str = DEFAULT_TOKEN
    log_path: str = "./"
    db_path: str = "./"
    admin_id: str = "447411595"  # @platun0v
    proxy: str = "socks5://127.0.0.1:9050"

    environment: str = "dev"

    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 1.0

    web_server_port: int = 9121
    web_server_host: str = "0.0.0.0"
    bot_url: str = "https://platun0v.ru"
    bot_url_path: str = "/give_money_bot"

    prometheus_port: int = web_server_port


cfg = Settings()

if cfg.telegram_token == DEFAULT_TOKEN:
    log.warning("Using default token. Bot wont work!")
