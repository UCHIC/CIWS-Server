import json
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
