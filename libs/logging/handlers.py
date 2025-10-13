import inspect
import logging

from loguru import logger


def safe_message(message):
    return message.replace("<", r"\<").replace(">", r"\>")


class LoguruHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(
            exception=record.exc_info,
            depth=depth,
            colors=True,
            lazy=True,
        ).log(level, safe_message(record.getMessage()))
