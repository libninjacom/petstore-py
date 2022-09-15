import logging

logger = logging.getLogger("petstore")


def enable_debug_logging() -> None:
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
