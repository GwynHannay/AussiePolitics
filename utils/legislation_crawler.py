import json
import logging
from utils import series, scrapy_helper, common, file_handler, tinydb_helper


logger = logging.getLogger(__name__)


def main(sections: list):
    full_config = load_config()
    logger.debug('Retrieved full config: %s', full_config)

    crawl_config = get_common_config(full_config)
    logger.debug('Extracted common config: %s', crawl_config)

    page_types = ['index', 'series', 'principal', 'details']

    for section in sections:
        piece = section.split('.')[0]
        crawl_config['section'] = full_config['index_urls'][piece]
        logger.debug('Built crawl config for piece %s: %s',
                     piece, crawl_config)
        logger.debug('Crawling these page types: %s', page_types)
        # crawl_section(section, crawl_config, page_types)
        # download_files(section)


def load_config() -> dict:
    """Opens the JSON file with our config and returns it as a dict.

    Raises:
        Exception: When failing to open the file specified.

    Returns:
        dict: Full contents of the JSON config.
    """
    config_file = 'config/legislation.json'
    try:
        with open(config_file) as f:
            configs = json.loads(f.read())
            return configs
    except Exception as e:
        logger.exception(
            'Failed getting file "%s" with error: %s', config_file, e)
        raise Exception

# TODO: Delete this if it's still commented out later
# def read_config(config: dict, sections: list) -> dict:
#     """Receives the full config and iterates through the sections of the legislation website
#     we are planning to scrape so return only the relevant parts of the config.

#     Args:
#         config (dict): Full config.
#         sections (list): Parts of the legislation website we're scraping, e.g. Acts, Bills.

#     Returns:
#         dict: Relevant config items only.
#     """
#     relevant_config = {}
#     for section in sections:
#         relevant_config[section] = config[section]

#     return relevant_config


def get_common_config(config: dict) -> dict:
    """Receives the full config and returns only the items applicable to all scraping.

    Args:
        config (dict): Full config.

    Raises:
        Exception: When attempting to pull common items out of config.

    Returns:
        dict: Relevant config items only.
    """
    try:
        common_config = {
            'base_url': config['base_url'],
            'index_url': {
                'prefix': config['index_urls']['prefix']
            },
            'section_urls': {
                'series': config['series_url'],
                'details': config['download_url']
            }
        }

        return common_config
    except Exception as e:
        logger.exception(
            'Problem retrieving config out of %s with error: %s', config, e)
        raise Exception


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
            series.add_principal_to_series(section)
            continue

        logger.debug('Fetching %s URLs for section "%s" with configs: %s',
                     page_type, section, crawl_config)
        urls = series.get_urls(page_type, section, crawl_config)

        if urls:
            logger.debug('Page type %s URLs passed along: %s', page_type, urls)
            scrapy_helper.run_scrapy(
                urls=urls, page_type=page_type, section=section)
        else:
            single_url = common.build_url_from_config(
                config=crawl_config, type=page_type)
            logger.debug('Page type %s, built single URL: %s',
                         page_type, single_url)
            scrapy_helper.run_scrapy(
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
    details_records = tinydb_helper.fetch_details_records(section)

    for record in details_records:
        updated_metadata = []

        try:
            for document in record['documents']:
                if document.get('download_link'):
                    downloaded = file_handler.download_file(
                        document['download_link'])
                    updated_metadata.append(document | downloaded)
                else:
                    logger.debug(
                        'No download link available for document %s', document['register_id'])
                    updated_metadata.append(document)

            logger.debug('Sending updated metadata for series "%s": %s',
                         record['series_id'], updated_metadata)
            tinydb_helper.update_list(updated_metadata, record['series_id'])
        except Exception as e:
            logger.exception(
                'Problem reading documents in this record: %s. Error was: %s', record, e)
            raise Exception
