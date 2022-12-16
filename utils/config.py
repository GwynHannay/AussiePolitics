import json
import os
import logging


CONFIG_DIR = 'config'
CRAWLER_CONFIG_FILE = 'legislation.json'
METADATA_CONFIG_FILE = 'metadata.json'

logger = logging.getLogger(__name__)


def init():
    global legislation_url_components
    global sections_to_crawl
    global stages
    global page_types
    global site_metadata

    legislation_url_components = set_configs('crawler')
    sections_to_crawl = set_sections_to_crawl()
    stages = set_stages()
    page_types = set_page_types()
    site_metadata = set_configs('metadata')


def set_configs(config_type: str) -> dict:
    try:
        if config_type == 'crawler':
            config_file_path = os.path.join(CONFIG_DIR, CRAWLER_CONFIG_FILE)
        elif config_type == 'metadata':
            config_file_path = os.path.join(CONFIG_DIR, METADATA_CONFIG_FILE)
        else:
            logger.exception('No valid config type issued to function, received %s', config_type)
            raise Exception

        with open(config_file_path) as f:
            configs = json.loads(f.read())
            return configs
    except Exception as e:
        logger.exception(
            'Failed getting config type "%s" from config directory "%s" with error: %s', config_type, CONFIG_DIR, e)
        raise Exception


def set_sections_to_crawl() -> list:
    return ['constitution']
    #return ['constitution', 'acts.in_force']


def set_stages() -> list:
    # return ['principal']
    return ['index', 'series', 'principal', 'details', 'download', 'diff']


def set_page_types() -> list:
    return ['index', 'series', 'details']


def set_current_section(new_section: str):
    global current_section
    current_section = new_section


def set_current_stage(new_stage: str):
    global current_stage
    current_stage = new_stage
