import logging
import sys
from types import FrameType
from typing import Optional

from loguru import logger

from give_money_bot.config import LOG_PATH


class InterceptHandler(logging.Handler):
    def emit(self, record):  # type: ignore
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


handler = InterceptHandler()
handler.setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)
logging.getLogger("sqlalchemy").setLevel(logging.INFO)
logging.getLogger("sqlalchemy").addHandler(handler)

logger.add(sys.stderr, level="DEBUG")
logger.add(LOG_PATH + "give_money_bot.log", level="DEBUG")
