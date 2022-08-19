import json
import logging


logger = logging.getLogger(__name__)
CONFIG_FILE = 'config/legislation.json'


def init():
    global legislation_url_components
    global sections_to_crawl
    global page_types

    legislation_url_components = set_crawler_configs()
    sections_to_crawl = set_sections_to_crawl()
    page_types = set_page_types()


def set_crawler_configs() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            configs = json.loads(f.read())
            return configs
    except Exception as e:
        logger.exception(
            'Failed getting file "%s" with error: %s', CONFIG_FILE, e)
        raise Exception


def set_sections_to_crawl() -> list:
    return ['constitution', 'acts.in_force']


def set_page_types() -> list:
    return ['index', 'series', 'principal', 'details']


def set_current_section(new_section: str):
    global current_section
    current_section = new_section


def set_current_page_type(new_page_type: str):
    global current_page_type
    current_page_type = new_page_type
