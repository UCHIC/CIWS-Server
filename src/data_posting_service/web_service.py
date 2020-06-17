import hashlib
import os
import sys
import json
from typing import Dict, List, Any, TextIO

import bottle


def get_app_config() -> Dict[str, Any]:
    settings_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data_loading_service', 'settings.json')
    data_file: TextIO

    with open(settings_path, 'r') as data_file:
        app_config: Dict[str, Any] = json.load(data_file)

    return app_config


# def authorize(passcode: str) -> bool:
#     token: str = config['upload_token'] if 'upload_token' in config else ''
#     hashed_passcode: str = hashlib.sha256(passcode.encode()).hexdigest()
#     return hashed_passcode == token

#err = HTTPError(401, text)
def get_file_save_directory() -> str:
    """ Gets the directory where the files will be copied to """

    default_directory: str = 'data'
    return config['local']['source'] if 'local' in config and 'source' in config['local'] else default_directory


# @bottle.get('/data-api')
# def data_api_details(filepath="data-api.html"):
#     return bottle.static_file(filepath, root='./content/')


@bottle.post('/data-api')
# @bottle.auth_basic(authorize)
def data_api_upload() -> Dict[str, str]:
    """ Saves csv files in the source folder for later processing """
    save_path: str = get_file_save_directory()
    uploaded_file: bottle.FileUpload
    messages: Dict[str, str] = {}
    name: str
    ext: str

    if 'data_file[]' not in bottle.request.files.dict:
        messages['no-file'] = 'No files to be uploaded.'
        return messages

    file_field: List[bottle.FileUpload] = bottle.request.files.dict['data_file[]']
    for uploaded_file in file_field:
        name, ext = os.path.splitext(uploaded_file.filename)
        if ext not in ('.csv',):
            messages[uploaded_file.filename] = f'File {uploaded_file.filename} has an unsupported file type: {ext}'
            continue
        try:
            uploaded_file.save(save_path)
            messages[uploaded_file.filename] = f'File {uploaded_file.filename} uploaded successfully'
        except IOError as ioe:
            messages[uploaded_file.filename] = f'File {uploaded_file.filename} not uploaded: {ioe}'

    return messages


try:
    config = get_app_config()
except IOError as ioe:
    sys.exit("Settings file not found!")

if __name__ == '__main__':
    """ Run locally on port 8080 if not run through a wsgi. """
    bottle.run(host='localhost', port=8080, debug=True)
else:
    """ Return wsgi application. """
    application = bottle.default_app()