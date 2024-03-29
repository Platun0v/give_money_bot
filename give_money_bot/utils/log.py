from loguru import logger

from give_money_bot.config import cfg

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


def init_logger() -> None:
    # logger.add(
    #     sys.stderr,
    #     backtrace=True,
    #     level="DEBUG",
    #     catch=True,
    # )
    logger.add(
        cfg.log_path + "give_money_bot.log",  # TODO: use union of paths
        backtrace=True,
        rotation="1 MB",
        level="DEBUG",
        catch=True,
        filter=lambda record: record["level"].name != "ERROR",
    )
    logger.add(  # Separate file for errors
        cfg.log_path + "give_money_bot_error.log",
        backtrace=True,
        rotation="1 MB",
        level="ERROR",
        catch=True,
    )
    # Add sqlalchemy logger

    # handler = InterceptHandler()
    # handler.setLevel(logging.DEBUG)
    # logging.getLogger().setLevel(logging.INFO)
    # logging.getLogger().addHandler(handler)
    # logging.getLogger("sqlalchemy").setLevel(logging.INFO)
    # logging.getLogger("sqlalchemy").addHandler(handler)
