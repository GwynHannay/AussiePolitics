import utils.docx_parser as docx
import utils.data_cleaner as dc

def main():
    doc = docx.open_document('hansard/C2021Q00024XN01.docx')
    text = docx.get_document_text(doc)

    i = 0
    for line in text:
        i = i + 1
        dc.remove_whitespace(line)
        if i > 500:
            break



if __name__ == "__main__":
    main()