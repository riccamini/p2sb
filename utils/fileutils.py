import os
import logging

logger = logging.getLogger(__name__)


def setup_dir(path: str):
    if path is None:
        logger.warning(f"Provided path is None!")
    elif not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

