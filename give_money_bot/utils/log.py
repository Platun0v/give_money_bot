import sys

from loguru import logger

from give_money_bot.config import LOG_PATH

# class InterceptHandler(logging.Handler):
#     def emit(self, record):  # type: ignore
#         # Get corresponding Loguru level if it exists
#         try:
#             level = logger.level(record.levelname).name
#         except ValueError:
#             level = record.levelno
#
#         # Find caller from where originated the logged message
#         frame, depth = logging.currentframe(), 2
#         while frame.f_code.co_filename == logging.__file__:
#             frame = frame.f_back  # type: ignore
#             depth += 1
#
#         logger.opt(depth=depth, exception=record.exc_info).log(
#             level, record.getMessage()
#         )

logger.add(sys.stderr, backtrace=True, level="DEBUG", catch=True)
logger.add(
    LOG_PATH + "give_money_bot.log", backtrace=True, rotation="1 MB", level="DEBUG", catch=True
)
