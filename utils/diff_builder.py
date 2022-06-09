import utils.docx_parser as docx
import difflib
import os
import re


diff_dir = 'changes'

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