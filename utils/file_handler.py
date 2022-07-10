import utils.docx_parser as docx
import difflib
import os
import re
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.request import urlretrieve


diff_dir = 'changes'


def download_file(document_metadata, filepath='docs'):
    download_link = document_metadata['Download Link']
    cache_filename = '.cache_constitution'
    _, headers = urlretrieve(download_link, cache_filename)
    content_disposition = headers.get('Content-Disposition')
    filename = re.findall(r'filename=([A-Za-z0-9]*\.docx)', content_disposition)
    content_type = headers.get('Content-Type')
    
    if filename and content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        new_filename = filename[0]
        with open(cache_filename, 'rb') as cached:
            file_content = cached.read()
            with open(os.path.join(filepath, new_filename), 'wb') as saved_file:
                saved_file.write(file_content)
        os.remove(cache_filename)

        document_metadata['Filename'] = new_filename
        document_metadata['Last Download Date'] = datetime.now(tz=ZoneInfo("Australia/Perth")).strftime('%d %b %Y %H:%M AWST')
        
        with open(os.path.join(filepath, ''.join([str(document_metadata['RegisterId']), '.json'])), 'w') as metadata_file:
            json.dump(document_metadata, metadata_file, ensure_ascii=False, indent=4)
    
    return document_metadata



def generate_diff_page(old_document, new_document, filepath):
    orig_doc = docx.open_document(os.path.join(filepath, old_document['Filename']))
    changed_doc = docx.open_document(os.path.join(filepath, new_document['Filename']))
    orig_text = docx.get_document_text(orig_doc)
    changed_text = docx.get_document_text(changed_doc)

    old_document_name = ''.join([old_document['Title'], ', Comp: ', old_document['Comp No.']])
    new_document_name = ''.join([new_document['Title'], ', Comp: ', new_document['Comp No.']])

    delta = difflib.HtmlDiff().make_file(orig_text, changed_text, old_document_name, new_document_name)
    delta_replaced = delta.replace('td.diff_header {text-align:right}', 'td.diff_header {text-align:center}').replace(' nowrap="nowrap"', '')
    delta_without_wrap = re.sub(r'(&nbsp;)([^&|<])', r' \2', delta_replaced)

    with open(os.path.join(diff_dir, ''.join([new_document['RegisterId'], '.html'])), 'w') as f:
        for line in delta_without_wrap:
            f.write(line)