import json
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Dict, Any, TextIO


def get_app_config() -> Dict[str, Any]:
    """
    Reads the settings.json file and loads all the app settings.
    """
    settings_path: Path = Path(__file__).resolve().parent / 'settings.json'
    data_file: TextIO

    with settings_path.open() as data_file:
        app_config: Dict[str, Any] = json.load(data_file)

    return app_config


def create_logger(app_name: str, logger_path: str) -> logging.Logger:
    """
    Create a logger with both a console and a time rotating file handler.
    """

    log: logging.Logger = logging.getLogger(app_name)
    log.setLevel(logging.DEBUG)

    # create console handler with a debug level
    ch: logging.StreamHandler = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Get logger path and create directories if it doesn't exist
    file_path: Path = Path(logger_path) / f'{app_name}.log'
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # create file handler with an error level
    fh: TimedRotatingFileHandler = TimedRotatingFileHandler(file_path, when='MIDNIGHT')
    fh.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    log.addHandler(fh)
    log.addHandler(ch)
    return log
