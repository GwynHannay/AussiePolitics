import re
import os
from urllib.request import urlretrieve


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
    