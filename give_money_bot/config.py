from loguru import logger as log
from pydantic_settings import BaseSettings, SettingsConfigDict

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


class BaseSettingsConfig:
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_file=".env",
        env_prefix="",
        extra="ignore",
    )


class Settings(BaseSettings, env_file=".env"):
    telegram_token: str = DEFAULT_TOKEN
    log_path: str = "./"
    db_path: str = "./"
    admin_id: str = "447411595"  # @platun0v
    proxy: str = "socks5://127.0.0.1:9050"

    environment: str = "dev"

    web_server_port: int = 9121
    web_server_host: str = "0.0.0.0"
    bot_url: str = "https://platun0v.ru"
    bot_url_path: str = "/give_money_bot"

    prometheus_port: int = web_server_port


cfg = Settings()

if cfg.telegram_token == DEFAULT_TOKEN:
    log.warning("Using default token. Bot wont work!")
