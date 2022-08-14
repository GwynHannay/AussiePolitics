import difflib
import logging
import os
import re
import helpers.docparser


logger = logging.getLogger(__name__)
DIFF_DIR = 'changes'


def generate_diff_page(old_document, new_document, filepath):
    orig_doc = helpers.docparser.open_document(os.path.join(filepath, old_document['Filename']))
    changed_doc = helpers.docparser.open_document(os.path.join(filepath, new_document['Filename']))
    orig_text = helpers.docparser.get_document_text(orig_doc)
    changed_text = helpers.docparser.get_document_text(changed_doc)

    old_document_name = ''.join([old_document['Title'], ', Comp: ', old_document['Comp No.']])
    new_document_name = ''.join([new_document['Title'], ', Comp: ', new_document['Comp No.']])

    delta = difflib.HtmlDiff().make_file(orig_text, changed_text, old_document_name, new_document_name)
    delta_replaced = delta.replace('td.diff_header {text-align:right}', 'td.diff_header {text-align:center}').replace(' nowrap="nowrap"', '')
    delta_without_wrap = re.sub(r'(&nbsp;)([^&|<])', r' \2', delta_replaced)

    with open(os.path.join(DIFF_DIR, ''.join([new_document['RegisterId'], '.html'])), 'w') as f:
        for line in delta_without_wrap:
            f.write(line)
