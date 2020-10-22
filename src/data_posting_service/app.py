import os
import json
from typing import Dict, Any, TextIO

from requestlogger import WSGILogger, ApacheFormatter
from logging.handlers import TimedRotatingFileHandler


def get_logging_middleware(app, config) -> WSGILogger:
    log_filename = config['log_filename'] if 'log_filename' in config else '/var/log/milton/logs.log'
    handlers = [TimedRotatingFileHandler(log_filename, 'd', 7), ]
    return WSGILogger(app, handlers, ApacheFormatter())


def get_app_config() -> Dict[str, Any]:
    settings_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
    data_file: TextIO

    with open(settings_path, 'r') as data_file:
        app_config: Dict[str, Any] = json.load(data_file)

    return app_config
