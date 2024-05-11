import logging

from loguru import logger


def setup_logger(level: str = "INFO"):
    logger.remove()
    logger.add(
        logging.StreamHandler(),
        format="{time} {level} {message} {extra}",
        level=level,
        serialize=True,
    )
