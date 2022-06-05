import utils.docx_parser as docx

def main():
    doc = docx.open_document('hansard/C2021Q00024XN01.docx')
    text = docx.get_document_text(doc)

    i = 0
    for line in text:
        i = i + 1
        print('breaker --')
        print(line)
        if i > 15:
            break



if __name__ == "__main__":
    main()