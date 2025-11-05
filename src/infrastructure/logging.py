import logging
from sys import stdout

from loguru import logger


def setup_logger(level: str = "INFO", serialize: bool = False):
    logger.remove()
    logger.add(
        logging.StreamHandler(stream=stdout),
        format="{time} {level} {message} {extra}",
        level=level,
        serialize=serialize,
    )
