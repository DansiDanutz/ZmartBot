from loguru import logger
import os

def setup_logging():
    level = os.getenv("LOG_LEVEL","INFO")
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), level=level)
    logger.info("Logging initialized at {}", level)
