import logging
import utils.config
import src.legislation_crawler


logger = logging.getLogger('main')


def main():
    utils.config.init()

    logger.debug('Begin crawl')
    src.legislation_crawler.main()

    # for document in constitution_metadata:
    #     document_order[document['Comp No.']] = completed_metadata
    #     time.sleep(crawl_delay)

    # previous_document = ''
    # for document in sorted(document_order):
    #     if document == '0':
    #         previous_document = document
    #         continue

    #     diff.generate_diff_page(document_order[previous_document], document_order[document], document_filepath)
    #     previous_document = document


if __name__ == "__main__":
    main()
