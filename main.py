import utils.docx_parser as docx
import utils.data_cleaner as dc
import utils.legislation_crawler as crawler
import difflib
import sys
import os
import json


def main():
    constitution_id = crawler.get_constitution()
    constitution_metadata = crawler.get_series(constitution_id)
    updated_metadata = []
    for document in constitution_metadata:
        metadata = crawler.get_download_details(document)
        updated_metadata.append(metadata)
        with open(''.join([document['RegisterId'], '.json']), 'w') as f:
            json.dump(metadata, f, ensure_ascii=False)


def build_diff():
    orig_doc = docx.open_document('hansard/The Constitution - as made version.docx')
    changed_doc = docx.open_document('hansard/C2021Q00024XN01.docx')
    orig_text = docx.get_document_text(orig_doc)
    changed_text = docx.get_document_text(changed_doc)

    # delta = difflib.HtmlDiff().make_table(orig_text, changed_text, 'Original Constitution', 'Constitution Changes')
    # with open('table.html', 'w') as f:
    #     f.write(delta)

    delta = difflib.unified_diff(orig_text, changed_text, 'Original Constitution', 'Constitution Changes')
    with open('changes.txt', 'w') as f:
        for line in delta:
            f.write(line)

    # i = 0
    # for line in orig_text:
    #     i = i + 1
    #     new_line = dc.remove_whitespace(line)
    #     if new_line.strip():
    #         print(new_line)
    #     if i > 500:
    #         break



if __name__ == "__main__":
    main()