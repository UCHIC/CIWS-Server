import logging
import os
import sys

import bottle

from typing import Dict, List, Any

from bottle import Request

from common import get_app_config, create_logger
from data_posting_service import auth


def log_to_logger(callback):
    def wrapper(*args, **kwargs):
        request: Request = bottle.request
        logger.info(f'{bottle.request.remote_addr} - {request.method} {request.path} : {bottle.response.status}')
        return callback(*args, **kwargs)
    return wrapper


# @bottle.get('/data-api')
# def data_api_details(filepath="data-api.html"):
#     return bottle.static_file(filepath, root='./content/')

@bottle.post('/auth')
def authorize_upload() -> str:
    """ Generates an upload token for a client """
    token: str = auth.generate_token()
    logger.info(f'upload token {token} generated for files {", ".join(bottle.request.forms.getall("filenames"))}')
    return token


@bottle.post('/data-api')
def data_api_upload() -> Dict[str, str]:
    """ Saves csv files in the source folder for later processing """
    auth.authorize()
    logger.info('data upload authorized!')

    save_path: str = config.get('source_directory', 'data')
    uploaded_file: bottle.FileUpload
    messages: Dict[str, str] = {}
    name: str
    ext: str

    files: List[bottle.FileUpload] = bottle.request.files.getall('data_file[]')

    if len(files) == 0:
        logger.warning('no files requested for upload.')
        messages['no-file'] = 'No files to be uploaded.'
        return messages

    for uploaded_file in files:
        name, ext = os.path.splitext(uploaded_file.filename)
        if ext.lower() not in ('.csv',):
            logger.warning(f'file {name} not uploaded because it has an unsupported file type: {ext}')
            messages[uploaded_file.filename] = f'File {uploaded_file.filename} has an unsupported file type: {ext}'
            continue
        try:
            logger.info(f'uploading file {uploaded_file.filename} to {save_path}')
            uploaded_file.save(save_path)
            logger.info(f'file {uploaded_file.filename} uploaded successfully!')
            messages[uploaded_file.filename] = f'File {uploaded_file.filename} uploaded successfully'
        except IOError as ioe:
            logger.error(f'file {uploaded_file.filename} could not be uploaded: {ioe}')
            messages[uploaded_file.filename] = f'File {uploaded_file.filename} not uploaded: {ioe}'

    logger.info('all files processed successfully')
    return messages


try:
    config: Dict[str, Any] = get_app_config()
except IOError as ioe:
    sys.exit("Settings file not found!")

logger: logging.Logger = create_logger('data_poster', config.get('log_directory'))
logger.info('logger started!')
application = bottle.default_app()
application.install(log_to_logger)


if __name__ == '__main__':
    # Run locally on port 8080 if not run through a wsgi.
    application.run(host='localhost', port=8080, debug=True)
