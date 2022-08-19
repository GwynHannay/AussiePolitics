import logging
import helpers.crawler
import helpers.db
import utils.common
import utils.config
import utils.downloader
import src.series


logger = logging.getLogger(__name__)


def main():
    website_sections = utils.config.sections_to_crawl

    for section in website_sections:
        utils.config.set_current_section(section)
        crawl_website_section()
            # crawl_section(section, crawl_config, page_types)
            # download_files(section)


def crawl_website_section():
    page_types = utils.config.page_types

    for page_type in page_types:
        utils.config.set_current_page_type(page_type)
        crawl_page_type()


def crawl_page_type():
    urls = get_urls()
    # run crawler
    # check for additional actions?
    # download files


def get_urls() -> list:
    page_type = utils.config.current_page_type
    match page_type:
        case 'index':
            urls = src.series.get_index_urls()
        case 'series':
            urls = src.series.get_metadata_urls()
        case 'details':
            urls = src.series.get_metadata_urls()
        case _:
            logger.exception('No valid page type given: %s', page_type)
            raise Exception
    
    return urls



def crawl_section(section: str, crawl_config: dict, page_types: list):
    """Iterates through each page type for a given section and directs scraping of metadata.

    Args:
        section (str): Part of the legislation website we're scraping, e.g. Acts In Force,
            Constitution.
        crawl_config (dict): Config items relevant to our scraping.
        page_types (list): Web page types, e.g. index, series, details.
    """    
    for page_type in page_types:
        if page_type == 'principal':
            logger.debug(
                'Adding Principal documents to each series in section "%s"', section)
            src.series.add_principal_to_series(section)
            continue

        logger.debug('Fetching %s URLs for section "%s" with configs: %s',
                     page_type, section, crawl_config)
        urls = src.series.get_urls(page_type, section, crawl_config)

        if urls:
            logger.debug('Page type %s URLs passed along: %s', page_type, urls)
            helpers.crawler.run_scrapy(
                urls=urls, page_type=page_type, section=section)
        else:
            single_url = utils.common.build_url_from_config(
                config=crawl_config, type=page_type)
            logger.debug('Page type %s, built single URL: %s',
                         page_type, single_url)
            helpers.crawler.run_scrapy(
                urls=[single_url], page_type=page_type, section=section)


def download_files(section: str):
    """Retrieves the metadata and directs the actual download of documents.

    Args:
        section (str): Part of the legislation website we're scraping, e.g. Acts In Force,
            Constitution.

    Raises:
        Exception: When unable to access the list of documents in a series.
    """    
    logger.debug('Fetching detailed DB records for section "%s"', section)
    details_records = helpers.db.fetch_details_records(section)

    for record in details_records:
        updated_metadata = []

        try:
            for document in record['documents']:
                if document.get('download_link'):
                    downloaded = utils.downloader.download_file(
                        document['download_link'])
                    updated_metadata.append(document | downloaded)
                else:
                    logger.debug(
                        'No download link available for document %s', document['register_id'])
                    updated_metadata.append(document)

            logger.debug('Sending updated metadata for series "%s": %s',
                         record['series_id'], updated_metadata)
            helpers.db.update_list(updated_metadata, record['series_id'])
        except Exception as e:
            logger.exception(
                'Problem reading documents in this record: %s. Error was: %s', record, e)
            raise Exception
