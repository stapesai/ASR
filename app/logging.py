# Path: app/logging.py
# Description: Logging configuration for the application.

import logging

# from fastapi.logger import logger

# TODO: Fix the logging, and use logging everywhere in application.
# TODO: This logger is not used in default fastapi logging.
# Do not remove this comment until logging is implemented everywhere in the application.
logging.basicConfig(
    # TODO: Take it from the environment variable.
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
)

# logger = logging.getLogger(__name__)
# logger = logging.getLogger("fastapi")
logger = logging.getLogger("uvicorn")

if __name__ == "__main__":
    # Log messages
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
