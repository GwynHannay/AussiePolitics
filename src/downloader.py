import logging
import re
import os
import helpers.db
from urllib.request import urlretrieve


logger = logging.getLogger(__name__)


def download_files():
    details_records = helpers.db.get_records_by_current_stage()

    for record in details_records:
        updated_metadata = []

        try:
            for document in record['documents']:
                if document.get('download_link'):
                    downloaded = download_file(document['download_link'])
                    updated_metadata.append(document | downloaded)
                else:
                    logger.debug(
                        'No download link available for document %s', document['register_id'])
                    updated_metadata.append(document)

            logger.debug('Sending updated metadata for series "%s": %s',
                         record['series_id'], updated_metadata)
            helpers.db.update_list(updated_metadata, record['series_id'])
        except Exception as e:
            logger.exception(
                'Problem reading documents in this record: %s. Error was: %s', record, e)
            raise Exception


def download_file(url: str) -> dict:
    cache_filename = '.cache_doc'
    _, headers = urlretrieve(url, cache_filename)
    content_disposition = headers.get('Content-Disposition')
    content_type = headers.get('Content-Type')
    
    filename = re.findall(r'filename=([A-Za-z0-9\.]*)$', content_disposition)[0]
    
    with open(cache_filename, 'rb') as cached:
        file_content = cached.read()
        with open(os.path.join('new_docs', filename), 'wb') as saved_file:
            saved_file.write(file_content)
    os.remove(cache_filename)

    download_metadata = {
        'filename': filename,
        'content_type': content_type
    }

    return download_metadata
    