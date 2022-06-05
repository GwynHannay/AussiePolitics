import docx


def open_document(filename: str):
    """Opens and returns a docx object (Microsoft Word)

    Args:
        filename (str): Full filename and path of docx file.

    Returns:
        |Document| object: docx object to be parsed.
    """
    return docx.Document(filename)


def get_header(document) -> list:
    """Grabs and returns a header object from each section of a docx object in a list.

    Args:
        document (|Document| object): docx object.

    Returns:
        list: Header object from each section within the docx object as a list item.
    """    
    headers = []
    for section in document.sections:
        headers.append(section.header)
    
    return headers


def get_footer(document) -> list:
    """Grabs and returns a footer object from each section of a docx object in a list.

    Args:
        document (|Document| object): docx object.

    Returns:
        list: Footer object from each section within the docx object as a list item.
    """   
    footers = []
    for section in document.sections:
        footers.append(section.footer)
    
    return footers


def get_document_text(docx_object) -> list:
    """Grabs and returns every paragraph in a docx document in a list.

    Args:
        document (|Document| OR _Header OR _Footer object): docx object.

    Returns:
        list: Text of each paragraph from the docx object as a list item.
    """
    text = []
    for paragraph in docx_object.paragraphs:
        text.append(paragraph.text)

    return text


def get_table_text(document) -> list:
    """Grabs and returns the text from each cell of each table from a docx object.

    Args:
        document (|Document| OR _Header OR _Footer object): docx object.

    Returns:
        list: Text from each cell of each row of each table in the docx object as a list inside a list inside a list.
    """
    table_text = []
    for tab in document.tables:
        row_text = []
        for row in tab.rows:
            cell_text = []
            for cell in row.cells:
                cell_text.append(cell.text)
            row_text.append(cell_text)
        table_text.append(row_text)

    return table_text


def get_inline_shapes(document) -> list:
    """Grabs and returns the type of each inline shape in a docx object.

    Args:
        document (|Document| OR _Header OR _Footer object): docx object.

    Returns:
        list: Each type of inline shape found in a docx object as a list item.
    """    
    shapes = []
    for shape in document.inline_shapes:
        shapes.append(shape.type)

    return shapes
