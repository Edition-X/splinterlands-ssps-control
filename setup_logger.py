#!/usr/bin/env python3
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if "DEBUG" in os.environ:
    logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d:%H-%M-%S")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)
