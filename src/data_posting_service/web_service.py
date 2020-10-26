import hashlib
import os
import sys
from typing import Dict, List, Any

import bottle
import canister

from data_posting_service import auth, app


def get_file_save_directory() -> str:
    """ Gets the directory where the files will be copied to """

    default_directory: str = 'data'
    return config['file_destination'] if 'file_destination' in config else default_directory


# @bottle.get('/data-api')
# def data_api_details(filepath="data-api.html"):
#     return bottle.static_file(filepath, root='./content/')

@bottle.post('/auth')
def authorize_upload() -> str:
    """ Generates an upload token for a client """
    return auth.generate_token()


@bottle.post('/data-api')
def data_api_upload() -> Dict[str, str]:
    """ Saves csv files in the source folder for later processing """
    auth.authorize()

    save_path: str = get_file_save_directory()
    uploaded_file: bottle.FileUpload
    messages: Dict[str, str] = {}
    name: str
    ext: str

    files: List[bottle.FileUpload] = bottle.request.files.getall('data_file[]')

    if len(files) == 0:
        messages['no-file'] = 'No files to be uploaded.'
        return messages

    for uploaded_file in files:
        name, ext = os.path.splitext(uploaded_file.filename)
        if ext.lower() not in ('.csv',):
            messages[uploaded_file.filename] = f'File {uploaded_file.filename} has an unsupported file type: {ext}'
            continue
        try:
            uploaded_file.save(save_path)
            messages[uploaded_file.filename] = f'File {uploaded_file.filename} uploaded successfully'
        except IOError as ioe:
            messages[uploaded_file.filename] = f'File {uploaded_file.filename} not uploaded: {ioe}'

    return messages


try:
    config: Dict[str, Any] = app.get_app_config()
except IOError as ioe:
    sys.exit("Settings file not found!")


application = bottle.default_app()
application.config.load_config(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bottle.conf'))
application.install(canister.Canister())

if __name__ == '__main__':
    """ Run locally on port 8080 if not run through a wsgi. """
    application.run(host='localhost', port=8080, debug=True)
