import os
import json
from typing import Dict, Any, TextIO



def get_app_config() -> Dict[str, Any]:
    settings_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
    data_file: TextIO

    with open(settings_path, 'r') as data_file:
        app_config: Dict[str, Any] = json.load(data_file)

    return app_config
