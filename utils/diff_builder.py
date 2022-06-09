import difflib


def generate_diff_page(old_document, new_document):
    print('Old')
    print(old_document['Filename'])
    print('New')
    print(new_document['Filename'])