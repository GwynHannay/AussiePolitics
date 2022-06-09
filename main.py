import utils.docx_parser as docx
import utils.data_cleaner as dc
import utils.legislation_crawler as crawler
import utils.diff_builder as diff
import difflib


document_filepath = 'docs'

def main():
    constitution_id = crawler.get_constitution()
    constitution_metadata = crawler.get_series(constitution_id)
    updated_metadata = []
    document_order = {}

    for document in constitution_metadata:
        download_page_metadata = crawler.get_download_details(document)
        completed_metadata = crawler.download_file(download_page_metadata, document_filepath)
        updated_metadata.append(completed_metadata)
        document_order[document['Comp No.']] = completed_metadata

    previous_document = ''
    for document in sorted(document_order):
        if document == '0':
            previous_document = document
            continue

        diff.generate_diff_page(document_order[previous_document], document_order[document])
        previous_document = document


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