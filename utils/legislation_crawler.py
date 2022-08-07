import json
from utils import series, scrapy_helper, common, file_handler, tinydb_helper


def main(sections: list):
    full_config = load_config()
    crawl_config = get_common_config(full_config)

    for section in sections:
        piece = section.split('.')[0]
        crawl_config['section'] = full_config['index_urls'][piece]
        # crawl_section(section, crawl_config)
        download_files(section)


def load_config() -> dict:
    """Opens the JSON file with our config and returns it as a dict.

    Returns:
        dict: Full contents of the JSON config.
    """
    with open('config/legislation.json') as f:
        configs = json.loads(f.read())
        return configs


def read_config(config: dict, sections: list) -> dict:
    """Receives the full config and iterates through the sections of the legislation website
    we are planning to scrape so return only the relevant parts of the config.

    Args:
        config (dict): Full config.
        sections (list): Parts of the legislation website we're scraping, e.g. Acts, Bills.

    Returns:
        dict: Relevant config items only.
    """
    relevant_config = {}
    for section in sections:
        relevant_config[section] = config[section]

    return relevant_config


def get_common_config(config: dict) -> dict:
    """Receives the full config and returns only the items applicable to all scraping.

    Args:
        config (dict): Full config.

    Returns:
        dict: Relevant config items only.
    """
    common_config = {
        'base_url': config['base_url'],
        'index_url': {
            'prefix': config['index_urls']['prefix']
        },
        'series_url': config['series_url'],
        'download_url': config['download_url']
    }
    return common_config


def crawl_section(section: str, crawl_config: dict):
    index_urls = series.get_indexes(section, crawl_config)

    if index_urls:
        scrapy_helper.run_scrapy(urls=index_urls, page_type='index', section=section)
    else:
        index_url = common.build_url_from_config(config=crawl_config, type='index')
        scrapy_helper.run_scrapy(urls=[index_url], page_type='index', section=section)

    series_urls = series.get_series(section, crawl_config)
    scrapy_helper.run_scrapy(urls=series_urls, page_type='series', section=section)
    series.add_principal_to_series(section)

    details_urls = series.get_details(section, crawl_config)
    scrapy_helper.run_scrapy(urls=[details_urls[2]], page_type='details', section=section)


def download_files(section: str):
    details_records = tinydb_helper.fetch_details_records(section)
    
    for record in details_records:
        updated_metadata = []
        for document in record['documents']:
            if document.get('download_link'):
                downloaded = file_handler.download_file(document['download_link'])
                updated_metadata.append(document | downloaded)
            else:
                updated_metadata.append(document)

        tinydb_helper.update_list(updated_metadata, record['series_id'])
